#!/usr/bin/env python3
"""
Basic ingestion script for loading synthetic contract data into FalkorDB.

This is a simplified version that doesn't use Graphiti's full episodic memory system,
but creates the basic graph structure for testing.

Usage:
    python scripts/ingest/basic_ingestion.py data/ground_truth/synthetic/matter_001_v1.json
"""

import json
import sys
from pathlib import Path
from falkordb import FalkorDB


def clean_string_for_cypher(s: str) -> str:
    """Escape single quotes in strings for Cypher queries"""
    return s.replace("'", "\\'").replace('"', '\\"').replace('\n', ' ')


def ingest_matter(matter_file: Path, graph_name: str = "negotiation_continuity"):
    """
    Ingest a single matter JSON file into FalkorDB.

    Args:
        matter_file: Path to JSON file
        graph_name: Name of the graph database
    """

    # Load data
    print(f"📄 Loading {matter_file.name}...")
    with open(matter_file) as f:
        data = json.load(f)

    matter_id = data["matter_id"]
    version = data["version"]

    print(f"   Matter: {matter_id} v{version}")
    print(f"   Clauses: {len(data['clauses'])}")
    print(f"   Recommendations: {len(data['recommendations'])}")
    print(f"   Decisions: {len(data['decisions'])}")
    print(f"   Concessions: {len(data['concessions'])}")

    # Connect to FalkorDB
    print(f"\n🔌 Connecting to FalkorDB...")
    db = FalkorDB(host='localhost', port=6379)
    graph = db.select_graph(graph_name)
    print(f"   Graph: {graph_name}")

    # Create Matter node
    print(f"\n📦 Creating Matter node...")
    matter_query = f"""
    CREATE (m:Matter {{
        matter_id: '{matter_id}',
        matter_type: '{data['matter_type']}',
        version: {version},
        timestamp: '{data['timestamp']}'
    }})
    """
    graph.query(matter_query)
    print(f"   ✅ Matter node created")

    # Create Party nodes
    print(f"\n👥 Creating Party nodes...")
    provider = data['parties']['provider']
    customer = data['parties']['customer']

    provider_query = f"""
    CREATE (p:Party {{
        name: '{provider['name']}',
        role: '{provider['role']}',
        matter_id: '{matter_id}'
    }})
    """
    graph.query(provider_query)

    customer_query = f"""
    CREATE (p:Party {{
        name: '{customer['name']}',
        role: '{customer['role']}',
        matter_id: '{matter_id}'
    }})
    """
    graph.query(customer_query)
    print(f"   ✅ 2 Party nodes created")

    # Create Clause nodes
    print(f"\n📋 Creating Clause nodes...")
    for i, clause in enumerate(data['clauses'], 1):
        # Truncate text for demo (avoid huge query strings)
        text_preview = clean_string_for_cypher(clause['text'][:200])

        clause_query = f"""
        CREATE (c:Clause {{
            clause_id: '{clause['clause_id']}',
            clause_number: '{clause['clause_number']}',
            title: '{clean_string_for_cypher(clause['title'])}',
            category: '{clean_string_for_cypher(clause['category'])}',
            text_preview: '{text_preview}...',
            version: {clause['version']},
            matter_id: '{matter_id}'
        }})
        """
        graph.query(clause_query)

        if i % 5 == 0 or i == len(data['clauses']):
            print(f"   Progress: {i}/{len(data['clauses'])} clauses")

    print(f"   ✅ {len(data['clauses'])} Clause nodes created")

    # Create Recommendation nodes
    if data['recommendations']:
        print(f"\n💡 Creating Recommendation nodes...")
        for i, rec in enumerate(data['recommendations'], 1):
            rec_query = f"""
            CREATE (r:Recommendation {{
                recommendation_id: '{rec['recommendation_id']}',
                clause_id: '{rec['clause_id']}',
                issue_type: '{clean_string_for_cypher(rec['issue_type'])}',
                classification: '{rec['classification']}',
                reasoning: '{clean_string_for_cypher(rec['reasoning'][:200])}...',
                matter_id: '{matter_id}'
            }})
            """
            graph.query(rec_query)

        print(f"   ✅ {len(data['recommendations'])} Recommendation nodes created")

        # Create relationships: Clause-[:HAS_RECOMMENDATION]->Recommendation
        print(f"\n🔗 Creating Clause-Recommendation relationships...")
        for rec in data['recommendations']:
            rel_query = f"""
            MATCH (c:Clause {{clause_id: '{rec['clause_id']}', matter_id: '{matter_id}'}}),
                  (r:Recommendation {{recommendation_id: '{rec['recommendation_id']}', matter_id: '{matter_id}'}})
            CREATE (c)-[:HAS_RECOMMENDATION]->(r)
            """
            graph.query(rel_query)

        print(f"   ✅ {len(data['recommendations'])} relationships created")

    # Create Decision nodes
    if data['decisions']:
        print(f"\n✅ Creating Decision nodes...")
        for i, dec in enumerate(data['decisions'], 1):
            notes = clean_string_for_cypher(dec.get('notes', '')[:200])

            dec_query = f"""
            CREATE (d:Decision {{
                decision_id: '{dec['decision_id']}',
                recommendation_id: '{dec['recommendation_id']}',
                decision_type: '{dec['decision_type']}',
                actor: '{dec['actor']}',
                role: '{dec['role']}',
                timestamp: '{dec['timestamp']}',
                notes: '{notes}',
                matter_id: '{matter_id}'
            }})
            """
            graph.query(dec_query)

        print(f"   ✅ {len(data['decisions'])} Decision nodes created")

        # Create relationships: Recommendation-[:HAS_DECISION]->Decision
        print(f"\n🔗 Creating Recommendation-Decision relationships...")
        for dec in data['decisions']:
            rel_query = f"""
            MATCH (r:Recommendation {{recommendation_id: '{dec['recommendation_id']}', matter_id: '{matter_id}'}}),
                  (d:Decision {{decision_id: '{dec['decision_id']}', matter_id: '{matter_id}'}})
            CREATE (r)-[:HAS_DECISION]->(d)
            """
            graph.query(rel_query)

        print(f"   ✅ {len(data['decisions'])} relationships created")

    # Create Concession nodes
    if data['concessions']:
        print(f"\n⚠️  Creating Concession nodes...")
        for i, con in enumerate(data['concessions'], 1):
            con_query = f"""
            CREATE (c:Concession {{
                concession_id: '{con['concession_id']}',
                decision_id: '{con['decision_id']}',
                clause_id: '{con['clause_id']}',
                description: '{clean_string_for_cypher(con['description'])}',
                impact: '{con['impact']}',
                rationale: '{clean_string_for_cypher(con['rationale'])}',
                matter_id: '{matter_id}'
            }})
            """
            graph.query(con_query)

        print(f"   ✅ {len(data['concessions'])} Concession nodes created")

        # Create relationships: Decision-[:RESULTED_IN_CONCESSION]->Concession
        print(f"\n🔗 Creating Decision-Concession relationships...")
        for con in data['concessions']:
            rel_query = f"""
            MATCH (d:Decision {{decision_id: '{con['decision_id']}', matter_id: '{matter_id}'}}),
                  (c:Concession {{concession_id: '{con['concession_id']}', matter_id: '{matter_id}'}})
            CREATE (d)-[:RESULTED_IN_CONCESSION]->(c)
            """
            graph.query(rel_query)

        print(f"   ✅ {len(data['concessions'])} relationships created")

    print(f"\n✅ Ingestion complete for {matter_id} v{version}!")
    return True


def verify_ingestion(matter_id: str, graph_name: str = "negotiation_continuity"):
    """Verify ingestion by querying the graph"""

    print(f"\n🔍 Verifying ingestion for {matter_id}...")

    db = FalkorDB(host='localhost', port=6379)
    graph = db.select_graph(graph_name)

    # Count nodes
    queries = {
        "Matters": f"MATCH (m:Matter {{matter_id: '{matter_id}'}}) RETURN COUNT(m)",
        "Parties": f"MATCH (p:Party {{matter_id: '{matter_id}'}}) RETURN COUNT(p)",
        "Clauses": f"MATCH (c:Clause {{matter_id: '{matter_id}'}}) RETURN COUNT(c)",
        "Recommendations": f"MATCH (r:Recommendation {{matter_id: '{matter_id}'}}) RETURN COUNT(r)",
        "Decisions": f"MATCH (d:Decision {{matter_id: '{matter_id}'}}) RETURN COUNT(d)",
        "Concessions": f"MATCH (c:Concession {{matter_id: '{matter_id}'}}) RETURN COUNT(c)",
    }

    for label, query in queries.items():
        result = graph.query(query)
        count = result.result_set[0][0] if result.result_set else 0
        print(f"   {label}: {count}")

    # Sample query: Find unfavorable recommendations
    print(f"\n📊 Sample Query: Unfavorable Recommendations")
    sample_query = f"""
    MATCH (c:Clause {{matter_id: '{matter_id}'}})-[:HAS_RECOMMENDATION]->(r:Recommendation {{classification: 'unfavorable'}})
    RETURN c.clause_number, c.title, r.issue_type
    LIMIT 3
    """
    result = graph.query(sample_query)

    if result.result_set:
        for row in result.result_set:
            print(f"   • Clause {row[0]}: {row[1]} - {row[2]}")
    else:
        print(f"   No unfavorable recommendations found")

    print(f"\n✅ Verification complete!")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/ingest/basic_ingestion.py <matter_file.json>")
        print("\nExample:")
        print("  python scripts/ingest/basic_ingestion.py data/ground_truth/synthetic/matter_001_v1.json")
        sys.exit(1)

    matter_file = Path(sys.argv[1])

    if not matter_file.exists():
        print(f"❌ Error: File not found: {matter_file}")
        sys.exit(1)

    print("="*80)
    print("BASIC FALKORDB INGESTION")
    print("="*80)
    print()

    try:
        # Load data from the JSON file
        with open(matter_file) as f:
            data = json.load(f)

        matter_id = data["matter_id"]

        # Ingest
        ingest_matter(matter_file)

        # Verify
        verify_ingestion(matter_id)

        print("\n" + "="*80)
        print("✅ SUCCESS!")
        print("="*80)
        print(f"\n💡 Next steps:")
        print(f"   1. Browse graph in FalkorDB UI: http://localhost:3000")
        print(f"   2. Run queries using Python or Cypher")
        print(f"   3. Ingest more matters to test cross-matter queries")

    except Exception as e:
        print(f"\n❌ Error during ingestion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
