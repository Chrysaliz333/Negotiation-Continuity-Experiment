#!/usr/bin/env python3
"""
Test queries to demonstrate graph database capabilities.

Usage:
    python scripts/test_queries.py
"""

from falkordb import FalkorDB


def run_query(graph, title, query, description=""):
    """Run a query and print results"""
    print(f"\n{'='*80}")
    print(f"QUERY: {title}")
    if description:
        print(f"Description: {description}")
    print(f"{'='*80}")
    print(f"\nCypher:\n{query}\n")

    result = graph.query(query)

    if result.result_set:
        print(f"Results ({len(result.result_set)} rows):")
        for i, row in enumerate(result.result_set, 1):
            print(f"  {i}. {' | '.join(str(v) for v in row)}")
    else:
        print("No results found.")

    return result


def main():
    print("="*80)
    print("NEGOTIATION CONTINUITY - TEST QUERIES")
    print("="*80)

    db = FalkorDB(host='localhost', port=6379)
    graph = db.select_graph('negotiation_continuity')

    # Query 1: Cross-version clause tracking
    run_query(
        graph,
        "Cross-Version Clause Tracking",
        """
        MATCH (c:Clause {matter_id: 'matter_001', clause_number: '1.1'})
        RETURN c.version, c.title, c.category
        ORDER BY c.version
        """,
        "Track how Clause 1.1 (Limitation of Liability) evolved across versions"
    )

    # Query 2: All unfavorable recommendations
    run_query(
        graph,
        "All Unfavorable Recommendations",
        """
        MATCH (c:Clause)-[:HAS_RECOMMENDATION]->(r:Recommendation {classification: 'unfavorable'})
        RETURN c.matter_id, c.clause_number, c.title, r.issue_type
        ORDER BY c.matter_id, c.clause_number
        LIMIT 10
        """,
        "Find all clauses flagged as unfavorable across all matters"
    )

    # Query 3: Decisions by actor
    run_query(
        graph,
        "Decisions by Jessica Martinez",
        """
        MATCH (d:Decision {actor: 'Jessica Martinez'})
        RETURN d.matter_id, d.decision_type, d.role, LEFT(d.notes, 50)
        ORDER BY d.matter_id
        """,
        "Track all decisions made by specific reviewer"
    )

    # Query 4: Concession analysis
    run_query(
        graph,
        "All Concessions",
        """
        MATCH (d:Decision)-[:RESULTED_IN_CONCESSION]->(con:Concession)
        RETURN con.matter_id, d.actor, con.description, con.impact, con.rationale
        """,
        "Find all concessions made during negotiations"
    )

    # Query 5: Recommendation coverage per matter
    run_query(
        graph,
        "Recommendation Coverage by Matter",
        """
        MATCH (m:Matter)
        OPTIONAL MATCH (c:Clause {matter_id: m.matter_id})-[:HAS_RECOMMENDATION]->(r:Recommendation)
        RETURN m.matter_id, m.version, COUNT(DISTINCT c) as total_clauses, COUNT(r) as recommendations
        ORDER BY m.matter_id, m.version
        """,
        "See how many clauses got recommendations in each version"
    )

    # Query 6: Override decisions (accepting unfavorable terms)
    run_query(
        graph,
        "Override Decisions on Unfavorable Terms",
        """
        MATCH (r:Recommendation {classification: 'unfavorable'})-[:HAS_DECISION]->(d:Decision {decision_type: 'override'})
        MATCH (c:Clause)-[:HAS_RECOMMENDATION]->(r)
        RETURN c.matter_id, c.clause_number, c.title, d.actor, LEFT(d.notes, 60)
        """,
        "Find cases where unfavorable recommendations were overridden (potential concessions)"
    )

    # Query 7: Clause categories distribution
    run_query(
        graph,
        "Clause Categories Distribution",
        """
        MATCH (c:Clause)
        RETURN c.category, COUNT(c) as count
        ORDER BY count DESC
        """,
        "Distribution of clause types across all matters"
    )

    # Query 8: Cross-matter precedent search
    run_query(
        graph,
        "Cross-Matter Precedent: Liability Clauses",
        """
        MATCH (c:Clause)
        WHERE c.title CONTAINS 'Liability'
        RETURN c.matter_id, c.version, c.clause_number, c.title, c.category
        ORDER BY c.matter_id, c.version
        """,
        "Find similar clauses across different matters (liability clauses)"
    )

    # Query 9: Decision type distribution
    run_query(
        graph,
        "Decision Type Distribution",
        """
        MATCH (d:Decision)
        RETURN d.decision_type, COUNT(d) as count
        ORDER BY count DESC
        """,
        "How were recommendations handled (apply vs override vs defer)?"
    )

    # Query 10: Recommendations without decisions (outstanding items)
    run_query(
        graph,
        "Outstanding Recommendations (No Decision Yet)",
        """
        MATCH (r:Recommendation)
        WHERE NOT (r)-[:HAS_DECISION]->(:Decision)
        MATCH (c:Clause)-[:HAS_RECOMMENDATION]->(r)
        RETURN c.matter_id, c.clause_number, c.title, r.classification, r.issue_type
        LIMIT 5
        """,
        "Find recommendations that haven't been acted upon"
    )

    print(f"\n{'='*80}")
    print("✅ ALL QUERIES COMPLETED")
    print(f"{'='*80}")
    print("\n💡 You can now:")
    print("  1. Browse the graph visually: http://localhost:3000")
    print("  2. Write custom queries using the patterns above")
    print("  3. Build KPI measurement queries")
    print("  4. Implement the retrieval gateway for the application")


if __name__ == "__main__":
    main()
