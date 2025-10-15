#!/usr/bin/env python3
"""
Natural Language Query Interface for Negotiation Continuity System

Allows users to ask questions in plain English and get graph database results.

Usage:
    python scripts/nl_query.py "Show me all concessions"
    python scripts/nl_query.py "What did we agree to in round 2?"
    python scripts/nl_query.py "Find liability clauses"

Interactive mode:
    python scripts/nl_query.py
"""

import sys
import re
from typing import Dict, List, Tuple, Optional, Any
from falkordb import FalkorDB


class NaturalLanguageQueryInterface:
    """
    Natural language query interface using pattern matching and templates.

    This is a rule-based system that maps common questions to Cypher queries.
    For production use, could be enhanced with LLM-based query generation.
    """

    def __init__(self, graph_name: str = "negotiation_continuity"):
        self.db = FalkorDB(host='localhost', port=6379)
        self.graph = self.db.select_graph(graph_name)

        # Define query patterns and their Cypher translations
        self.query_patterns = self._build_query_patterns()

    def _build_query_patterns(self) -> List[Dict[str, Any]]:
        """Build list of query patterns with regex matching and Cypher templates"""

        return [
            # Concession queries
            {
                "patterns": [
                    r"show.*concession",
                    r"find.*concession",
                    r"list.*concession",
                    r"what concession",
                    r"all concession",
                    r"get.*concession"
                ],
                "description": "Find all concessions made during negotiations",
                "cypher": """
                    MATCH (d:Decision)-[:RESULTED_IN_CONCESSION]->(con:Concession)
                    MATCH (c:Clause {clause_id: con.clause_id})
                    RETURN con.matter_id as matter,
                           c.clause_number as clause,
                           c.title as clause_title,
                           d.actor as who_made_it,
                           con.description as what_happened,
                           con.impact as impact_level,
                           con.rationale as why,
                           d.timestamp as when
                    ORDER BY d.timestamp
                """,
                "formatter": self._format_concessions
            },

            # Round-based queries
            {
                "patterns": [
                    r"what.*(?:agree|agreed).*(?:round|version)\s*(\d+)",
                    r"show.*(?:round|version)\s*(\d+)",
                    r"(?:round|version)\s*(\d+).*(?:decision|change)",
                ],
                "description": "Show decisions made in a specific round/version",
                "cypher_template": """
                    MATCH (m:Matter {{version: {version}}})
                    MATCH (c:Clause {{matter_id: m.matter_id, version: {version}}})
                    OPTIONAL MATCH (c)-[:HAS_RECOMMENDATION]->(r:Recommendation)
                    OPTIONAL MATCH (r)-[:HAS_DECISION]->(d:Decision)
                    RETURN m.matter_id as matter,
                           m.version as version,
                           c.clause_number as clause,
                           c.title as clause_title,
                           r.classification as recommendation,
                           d.decision_type as decision,
                           d.actor as who_decided,
                           d.notes as notes
                    ORDER BY c.clause_number
                """,
                "formatter": self._format_round_decisions,
                "requires_params": True
            },

            # Clause search queries
            {
                "patterns": [
                    r"find.*(?:clause|clauses).*(?:about|contain|with|re:?)?\s+['\"]?(\w+)['\"]?",
                    r"show.*(?:clause|clauses).*(?:about|contain|with|re:?)?\s+['\"]?(\w+)['\"]?",
                    r"search.*(?:clause|clauses).*['\"]?(\w+)['\"]?",
                    r"(liability|indemnit|warrant|termination|payment|data|ip|intellectual)\s*clause"
                ],
                "description": "Find clauses containing specific terms",
                "cypher_template": """
                    MATCH (c:Clause)
                    WHERE toLower(c.title) CONTAINS toLower('{keyword}')
                       OR toLower(c.category) CONTAINS toLower('{keyword}')
                    RETURN DISTINCT c.matter_id as matter,
                           c.version as version,
                           c.clause_number as clause,
                           c.title as title,
                           c.category as category
                    ORDER BY c.matter_id, c.version, c.clause_number
                """,
                "formatter": self._format_clause_search,
                "requires_params": True
            },

            # Actor/reviewer queries
            {
                "patterns": [
                    r"(?:decision|review|work).*(?:by|from|made by)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
                    r"what.*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:decide|review|do)",
                    r"show.*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'?s?\s+(?:decision|review|work)"
                ],
                "description": "Show decisions made by a specific person",
                "cypher_template": """
                    MATCH (d:Decision {{actor: '{actor}'}})
                    MATCH (r:Recommendation)-[:HAS_DECISION]->(d)
                    MATCH (c:Clause)-[:HAS_RECOMMENDATION]->(r)
                    RETURN d.matter_id as matter,
                           c.clause_number as clause,
                           c.title as clause_title,
                           r.classification as recommendation_type,
                           d.decision_type as decision,
                           d.timestamp as when,
                           LEFT(d.notes, 100) as notes
                    ORDER BY d.timestamp
                """,
                "formatter": self._format_actor_decisions,
                "requires_params": True
            },

            # Unfavorable terms queries
            {
                "patterns": [
                    r"unfavorable",
                    r"(?:bad|problematic|risky)\s+(?:term|clause)",
                    r"(?:issue|problem|concern|risk).*clause"
                ],
                "description": "Find all unfavorable terms flagged in reviews",
                "cypher": """
                    MATCH (c:Clause)-[:HAS_RECOMMENDATION]->(r:Recommendation {classification: 'unfavorable'})
                    OPTIONAL MATCH (r)-[:HAS_DECISION]->(d:Decision)
                    RETURN c.matter_id as matter,
                           c.version as version,
                           c.clause_number as clause,
                           c.title as clause_title,
                           r.issue_type as issue,
                           d.decision_type as decision,
                           d.actor as reviewed_by
                    ORDER BY c.matter_id, c.version, c.clause_number
                    LIMIT 20
                """,
                "formatter": self._format_unfavorable_terms
            },

            # Matter overview queries
            {
                "patterns": [
                    r"(?:overview|summary|status).*(?:matter|contract)\s+(\w+)",
                    r"(?:matter|contract)\s+(\w+)\s+(?:overview|summary|status)",
                    r"show.*(?:matter|contract)\s+(\w+)"
                ],
                "description": "Show overview of a specific matter",
                "cypher_template": """
                    MATCH (m:Matter {{matter_id: '{matter_id}'}})
                    OPTIONAL MATCH (c:Clause {{matter_id: '{matter_id}', version: m.version}})
                    OPTIONAL MATCH (c)-[:HAS_RECOMMENDATION]->(r:Recommendation)
                    OPTIONAL MATCH (r)-[:HAS_DECISION]->(d:Decision)
                    OPTIONAL MATCH (d)-[:RESULTED_IN_CONCESSION]->(con:Concession)
                    RETURN m.matter_id as matter,
                           m.version as version,
                           m.matter_type as type,
                           m.timestamp as last_updated,
                           COUNT(DISTINCT c) as total_clauses,
                           COUNT(DISTINCT r) as recommendations,
                           COUNT(DISTINCT d) as decisions,
                           COUNT(DISTINCT con) as concessions
                    ORDER BY m.version
                """,
                "formatter": self._format_matter_overview,
                "requires_params": True
            },

            # Cross-version tracking queries
            {
                "patterns": [
                    r"(?:track|history|evolution).*clause\s+([\d.]+)",
                    r"clause\s+([\d.]+).*(?:change|history|version)",
                    r"how.*clause\s+([\d.]+).*(?:change|evolve)"
                ],
                "description": "Track how a specific clause evolved across versions",
                "cypher_template": """
                    MATCH (c:Clause {{clause_number: '{clause_number}'}})
                    OPTIONAL MATCH (c)-[:HAS_RECOMMENDATION]->(r:Recommendation)
                    OPTIONAL MATCH (r)-[:HAS_DECISION]->(d:Decision)
                    RETURN c.matter_id as matter,
                           c.version as version,
                           c.clause_number as clause,
                           c.title as title,
                           r.classification as recommendation,
                           r.issue_type as issue,
                           d.decision_type as decision
                    ORDER BY c.matter_id, c.version
                """,
                "formatter": self._format_clause_history,
                "requires_params": True
            },

            # Statistics queries
            {
                "patterns": [
                    r"(?:statistics|stats|count)",
                    r"how many",
                    r"total.*(?:clause|recommendation|decision|concession)"
                ],
                "description": "Show overall system statistics",
                "cypher": """
                    MATCH (m:Matter)
                    WITH COUNT(DISTINCT m) as matters
                    MATCH (p:Party)
                    WITH matters, COUNT(DISTINCT p) as parties
                    MATCH (c:Clause)
                    WITH matters, parties, COUNT(DISTINCT c) as clauses
                    OPTIONAL MATCH (r:Recommendation)
                    WITH matters, parties, clauses, COUNT(DISTINCT r) as recommendations
                    OPTIONAL MATCH (d:Decision)
                    WITH matters, parties, clauses, recommendations, COUNT(DISTINCT d) as decisions
                    OPTIONAL MATCH (con:Concession)
                    RETURN matters, parties, clauses, recommendations, decisions, COUNT(DISTINCT con) as concessions
                """,
                "formatter": self._format_statistics
            },

            # Decision distribution queries
            {
                "patterns": [
                    r"decision.*(?:distribution|breakdown|type)",
                    r"(?:apply|override|defer).*decision"
                ],
                "description": "Show breakdown of decision types",
                "cypher": """
                    MATCH (d:Decision)
                    WITH COUNT(d) as total
                    MATCH (d2:Decision)
                    WITH d2.decision_type as decision_type, COUNT(d2) as count, total
                    RETURN decision_type, count, ROUND(100.0 * count / total) as percentage
                    ORDER BY count DESC
                """,
                "formatter": self._format_decision_distribution
            }
        ]

    def match_query(self, question: str) -> Optional[Tuple[Dict[str, Any], Dict[str, str]]]:
        """
        Match a natural language question to a query pattern.

        Returns:
            Tuple of (pattern_dict, params_dict) if match found, None otherwise
        """
        question_lower = question.lower().strip()

        for pattern_dict in self.query_patterns:
            for pattern in pattern_dict["patterns"]:
                match = re.search(pattern, question_lower)
                if match:
                    # Extract parameters from regex groups
                    params = {}
                    if match.groups():
                        if "round" in pattern or "version" in pattern:
                            params["version"] = int(match.group(1))
                        elif "clause" in pattern and "clause_number" in pattern_dict.get("cypher_template", ""):
                            params["clause_number"] = match.group(1)
                        elif "matter" in pattern:
                            params["matter_id"] = match.group(1)
                        elif "actor" in pattern_dict.get("cypher_template", ""):
                            params["actor"] = match.group(1).title()  # Capitalize name
                        else:
                            # Generic keyword extraction
                            params["keyword"] = match.group(1)
                    else:
                        # No capture groups - check if template needs keyword
                        if "keyword" in pattern_dict.get("cypher_template", ""):
                            # Try to infer keyword from pattern or question
                            # Extract common terms like "liability", "indemnity", etc.
                            for term in ["liability", "indemnit", "warrant", "termination", "payment", "data", "ip", "intellectual"]:
                                if term in question_lower:
                                    params["keyword"] = term
                                    break

                    return (pattern_dict, params)

        return None

    def execute_query(self, question: str) -> Dict[str, Any]:
        """
        Execute a natural language query and return formatted results.

        Returns:
            Dictionary with query results and metadata
        """
        # Try to match question to a pattern
        match_result = self.match_query(question)

        if not match_result:
            return {
                "success": False,
                "error": "Could not understand the question",
                "suggestions": self._get_example_questions()
            }

        pattern_dict, params = match_result

        # Build Cypher query
        if "cypher" in pattern_dict:
            cypher_query = pattern_dict["cypher"]
        elif "cypher_template" in pattern_dict:
            # Check if we have all required parameters
            template = pattern_dict["cypher_template"]
            # Extract required parameters from template
            import string
            required_params = [fname for _, fname, _, _ in string.Formatter().parse(template) if fname]

            # Fill in missing params with empty strings or defaults
            for param in required_params:
                if param not in params:
                    # Try to infer from question
                    if param == "keyword":
                        # Extract any word from the question that's not a common word
                        common_words = {"find", "show", "get", "list", "all", "the", "a", "an", "clause", "clauses"}
                        words = question.lower().split()
                        for word in words:
                            if word not in common_words and len(word) > 2:
                                params[param] = word
                                break
                        if param not in params:
                            params[param] = ""

            cypher_query = template.format(**params)
        else:
            return {
                "success": False,
                "error": "Query pattern configuration error"
            }

        # Execute query
        try:
            result = self.graph.query(cypher_query)

            # Format results
            formatter = pattern_dict.get("formatter", self._format_generic)
            formatted_output = formatter(result.result_set, params)

            return {
                "success": True,
                "question": question,
                "description": pattern_dict["description"],
                "results_count": len(result.result_set),
                "results": formatted_output,
                "cypher": cypher_query  # Include for debugging
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Query execution error: {str(e)}",
                "cypher": cypher_query
            }

    # =========================================================================
    # Result Formatters
    # =========================================================================

    def _format_concessions(self, rows: List, params: Dict) -> str:
        """Format concession query results"""
        if not rows:
            return "No concessions found in the database."

        output = []
        output.append(f"\n🔍 Found {len(rows)} concession(s):\n")

        for i, row in enumerate(rows, 1):
            matter, clause, title, who, what, impact, why, when = row
            output.append(f"{i}. {matter} - Clause {clause}: {title}")
            output.append(f"   Who: {who}")
            output.append(f"   What: {what}")
            output.append(f"   Impact: {impact}")
            output.append(f"   Rationale: {why}")
            output.append(f"   When: {when}")
            output.append("")

        return "\n".join(output)

    def _format_round_decisions(self, rows: List, params: Dict) -> str:
        """Format round-based decision results"""
        if not rows:
            return f"No decisions found for version {params.get('version', '?')}."

        version = params.get("version", "?")
        output = []
        output.append(f"\n📋 Decisions in Round/Version {version}:\n")

        for i, row in enumerate(rows, 1):
            matter, ver, clause, title, rec, decision, who, notes = row
            if decision:  # Only show clauses with decisions
                output.append(f"{i}. Clause {clause}: {title}")
                output.append(f"   Recommendation: {rec or 'None'}")
                output.append(f"   Decision: {decision} (by {who})")
                if notes:
                    output.append(f"   Notes: {notes}")
                output.append("")

        return "\n".join(output) if len(output) > 2 else f"No decisions recorded for version {version}."

    def _format_clause_search(self, rows: List, params: Dict) -> str:
        """Format clause search results"""
        if not rows:
            keyword = params.get("keyword", "?")
            return f"No clauses found containing '{keyword}'."

        keyword = params.get("keyword", "")
        output = []
        output.append(f"\n🔍 Found {len(rows)} clause(s) matching '{keyword}':\n")

        for i, row in enumerate(rows, 1):
            matter, version, clause, title, category = row
            output.append(f"{i}. {matter} v{version} - Clause {clause}: {title}")
            output.append(f"   Category: {category}")
            output.append("")

        return "\n".join(output)

    def _format_actor_decisions(self, rows: List, params: Dict) -> str:
        """Format actor-specific decision results"""
        if not rows:
            actor = params.get("actor", "?")
            return f"No decisions found for {actor}."

        actor = params.get("actor", "?")
        output = []
        output.append(f"\n👤 Decisions by {actor}:\n")

        for i, row in enumerate(rows, 1):
            matter, clause, title, rec_type, decision, when, notes = row
            output.append(f"{i}. {matter} - Clause {clause}: {title}")
            output.append(f"   Recommendation type: {rec_type}")
            output.append(f"   Decision: {decision}")
            output.append(f"   When: {when}")
            if notes:
                output.append(f"   Notes: {notes}...")
            output.append("")

        return "\n".join(output)

    def _format_unfavorable_terms(self, rows: List, params: Dict) -> str:
        """Format unfavorable terms results"""
        if not rows:
            return "No unfavorable terms found."

        output = []
        output.append(f"\n⚠️  Found {len(rows)} unfavorable term(s):\n")

        for i, row in enumerate(rows, 1):
            matter, version, clause, title, issue, decision, reviewer = row
            output.append(f"{i}. {matter} v{version} - Clause {clause}: {title}")
            output.append(f"   Issue: {issue}")
            output.append(f"   Decision: {decision or 'Pending'} {f'by {reviewer}' if reviewer else ''}")
            output.append("")

        return "\n".join(output)

    def _format_matter_overview(self, rows: List, params: Dict) -> str:
        """Format matter overview results"""
        if not rows:
            matter_id = params.get("matter_id", "?")
            return f"Matter {matter_id} not found."

        output = []
        output.append(f"\n📊 Matter Overview:\n")

        for row in rows:
            matter, version, mtype, updated, clauses, recs, decisions, concessions = row
            output.append(f"Matter: {matter} (Version {version})")
            output.append(f"Type: {mtype}")
            output.append(f"Last updated: {updated}")
            output.append(f"")
            output.append(f"Statistics:")
            output.append(f"  - Clauses: {clauses}")
            output.append(f"  - Recommendations: {recs}")
            output.append(f"  - Decisions: {decisions}")
            output.append(f"  - Concessions: {concessions}")
            output.append("")

        return "\n".join(output)

    def _format_clause_history(self, rows: List, params: Dict) -> str:
        """Format clause history results"""
        if not rows:
            clause_num = params.get("clause_number", "?")
            return f"No history found for clause {clause_num}."

        clause_num = params.get("clause_number", "?")
        output = []
        output.append(f"\n📜 History of Clause {clause_num}:\n")

        for i, row in enumerate(rows, 1):
            matter, version, clause, title, rec, issue, decision = row
            output.append(f"{i}. Version {version} ({matter}): {title}")
            if rec:
                output.append(f"   Recommendation: {rec} ({issue})")
                output.append(f"   Decision: {decision or 'Pending'}")
            else:
                output.append(f"   No recommendations")
            output.append("")

        return "\n".join(output)

    def _format_statistics(self, rows: List, params: Dict) -> str:
        """Format statistics results"""
        if not rows:
            return "No statistics available."

        row = rows[0]
        matters, parties, clauses, recs, decisions, concessions = row

        output = []
        output.append("\n📊 System Statistics:\n")
        output.append(f"Matters: {matters}")
        output.append(f"Parties: {parties}")
        output.append(f"Clauses: {clauses}")
        output.append(f"Recommendations: {recs}")
        output.append(f"Decisions: {decisions}")
        output.append(f"Concessions: {concessions}")
        output.append("")

        return "\n".join(output)

    def _format_decision_distribution(self, rows: List, params: Dict) -> str:
        """Format decision distribution results"""
        if not rows:
            return "No decision data available."

        output = []
        output.append("\n📊 Decision Distribution:\n")

        for row in rows:
            decision_type, count, percentage = row
            output.append(f"{decision_type}: {count} ({percentage}%)")

        output.append("")
        return "\n".join(output)

    def _format_generic(self, rows: List, params: Dict) -> str:
        """Generic formatter for unformatted results"""
        if not rows:
            return "No results found."

        output = []
        output.append(f"\n📋 Found {len(rows)} result(s):\n")

        for i, row in enumerate(rows, 1):
            output.append(f"{i}. {' | '.join(str(v) for v in row)}")

        output.append("")
        return "\n".join(output)

    def _get_example_questions(self) -> List[str]:
        """Return list of example questions"""
        return [
            "Show me all concessions",
            "What did we agree to in round 2?",
            "Find liability clauses",
            "What did Sarah Chen decide?",
            "Show unfavorable terms",
            "Overview of matter_001",
            "Track clause 1.1 history",
            "How many clauses are there?",
            "Show decision distribution"
        ]

    def print_help(self):
        """Print help information"""
        print("\n" + "="*80)
        print("NATURAL LANGUAGE QUERY INTERFACE")
        print("="*80)
        print("\nYou can ask questions in plain English. Here are some examples:\n")

        for example in self._get_example_questions():
            print(f"  • {example}")

        print("\nSupported query types:")
        print("  • Concession tracking")
        print("  • Round-based decisions")
        print("  • Clause search")
        print("  • Actor/reviewer activity")
        print("  • Unfavorable terms")
        print("  • Matter overviews")
        print("  • Clause history")
        print("  • Statistics")
        print("\nType 'help' for this message, 'quit' or 'exit' to quit.\n")


def main():
    """Main entry point"""
    print("="*80)
    print("NATURAL LANGUAGE QUERY INTERFACE")
    print("="*80)

    # Initialize interface
    interface = NaturalLanguageQueryInterface()

    # Check if question provided as argument
    if len(sys.argv) > 1:
        # Single query mode
        question = " ".join(sys.argv[1:])

        result = interface.execute_query(question)

        if result["success"]:
            print(f"\n📝 Question: {result['question']}")
            print(f"💡 Interpretation: {result['description']}")
            print(result["results"])
        else:
            print(f"\n❌ Error: {result['error']}")
            if "suggestions" in result:
                print("\n💡 Try questions like:")
                for example in result["suggestions"][:5]:
                    print(f"  • {example}")
    else:
        # Interactive mode
        interface.print_help()

        while True:
            try:
                question = input("❓ Ask a question (or 'help', 'quit'): ").strip()

                if not question:
                    continue

                if question.lower() in ["quit", "exit", "q"]:
                    print("\n👋 Goodbye!")
                    break

                if question.lower() in ["help", "h", "?"]:
                    interface.print_help()
                    continue

                # Execute query
                result = interface.execute_query(question)

                if result["success"]:
                    print(f"\n💡 {result['description']}")
                    print(result["results"])
                else:
                    print(f"\n❌ {result['error']}")
                    if "suggestions" in result:
                        print("\n💡 Try questions like:")
                        for example in result["suggestions"][:3]:
                            print(f"  • {example}")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
