#!/usr/bin/env python3
"""
Export local FalkorDB graph and upload to FalkorDB Cloud

This script:
1. Connects to your local FalkorDB instance
2. Extracts all nodes and relationships
3. Uploads them to your FalkorDB Cloud instance

Usage:
    # First, set environment variables in .env:
    # FALKORDB_CLOUD_HOST=your-instance.falkordb.cloud
    # FALKORDB_CLOUD_PORT=6379
    # FALKORDB_CLOUD_PASSWORD=your-password

    python3 scripts/export_to_cloud.py
"""

import os
import sys
from pathlib import Path
from falkordb import FalkorDB
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Cloud connection settings
CLOUD_HOST = os.getenv('FALKORDB_CLOUD_HOST')
CLOUD_PORT = int(os.getenv('FALKORDB_CLOUD_PORT', '6379'))
CLOUD_PASSWORD = os.getenv('FALKORDB_CLOUD_PASSWORD')

# Local connection settings
LOCAL_HOST = 'localhost'
LOCAL_PORT = 6379

# Graph name
GRAPH_NAME = 'negotiation_continuity'


def check_cloud_credentials():
    """Verify cloud credentials are set"""
    if not CLOUD_HOST or not CLOUD_PASSWORD:
        print("❌ Error: FalkorDB Cloud credentials not set!")
        print("\nPlease add to your .env file:")
        print("  FALKORDB_CLOUD_HOST=your-instance.falkordb.cloud")
        print("  FALKORDB_CLOUD_PORT=6379")
        print("  FALKORDB_CLOUD_PASSWORD=your-password")
        print("\nYou can find these in your FalkorDB Cloud dashboard.")
        sys.exit(1)


def connect_to_local():
    """Connect to local FalkorDB"""
    try:
        print(f"📡 Connecting to local FalkorDB at {LOCAL_HOST}:{LOCAL_PORT}...")
        db = FalkorDB(host=LOCAL_HOST, port=LOCAL_PORT)
        graph = db.select_graph(GRAPH_NAME)

        # Test connection
        result = graph.query('MATCH (n) RETURN COUNT(n) as count')
        node_count = result.result_set[0][0]

        print(f"✅ Connected to local FalkorDB")
        print(f"   Graph: {GRAPH_NAME}")
        print(f"   Nodes: {node_count}")

        return db, graph
    except Exception as e:
        print(f"❌ Failed to connect to local FalkorDB: {e}")
        print("\nMake sure FalkorDB is running:")
        print("  docker start falkordb")
        sys.exit(1)


def connect_to_cloud():
    """Connect to FalkorDB Cloud"""
    try:
        print(f"\n📡 Connecting to FalkorDB Cloud at {CLOUD_HOST}...")
        db = FalkorDB(
            host=CLOUD_HOST,
            port=CLOUD_PORT,
            password=CLOUD_PASSWORD,
            ssl=True
        )

        # Test connection
        db.ping()

        print(f"✅ Connected to FalkorDB Cloud")

        return db
    except Exception as e:
        print(f"❌ Failed to connect to FalkorDB Cloud: {e}")
        print("\nPlease verify:")
        print("  1. Your cloud instance is running")
        print("  2. Credentials in .env are correct")
        print("  3. Network connection is stable")
        sys.exit(1)


def clear_cloud_graph(cloud_db):
    """Clear existing data in cloud graph (optional, ask user first)"""
    response = input("\n⚠️  Clear existing data in cloud? (y/N): ").strip().lower()

    if response == 'y':
        print("🗑️  Clearing cloud graph...")
        try:
            cloud_graph = cloud_db.select_graph(GRAPH_NAME)
            cloud_graph.query('MATCH (n) DETACH DELETE n')
            print("✅ Cloud graph cleared")
        except Exception as e:
            print(f"⚠️  Could not clear graph (may not exist yet): {e}")


def copy_nodes(local_graph, cloud_db):
    """Copy all nodes from local to cloud"""
    print("\n📦 Copying nodes to cloud...")

    cloud_graph = cloud_db.select_graph(GRAPH_NAME)

    node_types = ['Matter', 'Party', 'Clause', 'Recommendation', 'Decision', 'Concession']

    total_nodes = 0

    for node_type in node_types:
        print(f"  Copying {node_type} nodes...", end=' ', flush=True)

        # Get all nodes of this type from local
        result = local_graph.query(f'MATCH (n:{node_type}) RETURN n')

        count = 0
        for row in result.result_set:
            node = row[0]
            props = node.properties

            # Build property string for CREATE
            prop_parts = []
            for key, value in props.items():
                if isinstance(value, str):
                    # Escape quotes
                    value = value.replace('\\', '\\\\').replace('"', '\\"')
                    prop_parts.append(f'{key}: "{value}"')
                elif isinstance(value, bool):
                    prop_parts.append(f'{key}: {str(value).lower()}')
                elif value is not None:
                    prop_parts.append(f'{key}: {value}')

            props_str = ', '.join(prop_parts)

            # Create node in cloud
            create_query = f'CREATE (:{node_type} {{{props_str}}})'
            cloud_graph.query(create_query)

            count += 1

        print(f"✅ {count} nodes")
        total_nodes += count

    print(f"\n✅ Total nodes copied: {total_nodes}")
    return total_nodes


def copy_relationships(local_graph, cloud_db):
    """Copy all relationships from local to cloud"""
    print("\n🔗 Copying relationships to cloud...")

    cloud_graph = cloud_db.select_graph(GRAPH_NAME)

    rel_types = ['HAS_RECOMMENDATION', 'HAS_DECISION', 'RESULTED_IN_CONCESSION']

    total_rels = 0

    for rel_type in rel_types:
        print(f"  Copying {rel_type} relationships...", end=' ', flush=True)

        # Get all relationships of this type
        result = local_graph.query(f'''
            MATCH (a)-[r:{rel_type}]->(b)
            RETURN labels(a)[0] as from_type,
                   a as from_node,
                   labels(b)[0] as to_type,
                   b as to_node
        ''')

        count = 0
        for row in result.result_set:
            from_type = row[0]
            from_node = row[1]
            to_type = row[2]
            to_node = row[3]

            # Get ID properties
            from_id = get_id_property(from_type, from_node.properties)
            to_id = get_id_property(to_type, to_node.properties)

            # Create relationship in cloud
            create_query = f'''
                MATCH (a:{from_type} {{{from_id}}}), (b:{to_type} {{{to_id}}})
                CREATE (a)-[:{rel_type}]->(b)
            '''
            cloud_graph.query(create_query)

            count += 1

        print(f"✅ {count} relationships")
        total_rels += count

    print(f"\n✅ Total relationships copied: {total_rels}")
    return total_rels


def get_id_property(node_type, properties):
    """Get the ID property string for a node"""
    id_fields = {
        'Matter': 'matter_id',
        'Party': 'party_id',
        'Clause': 'clause_id',
        'Recommendation': 'recommendation_id',
        'Decision': 'decision_id',
        'Concession': 'concession_id'
    }

    id_field = id_fields.get(node_type, 'id')
    id_value = properties.get(id_field, '')

    # Escape quotes in ID value
    id_value = id_value.replace('\\', '\\\\').replace('"', '\\"')

    return f'{id_field}: "{id_value}"'


def verify_cloud_data(cloud_db):
    """Verify data was copied correctly"""
    print("\n🔍 Verifying cloud data...")

    cloud_graph = cloud_db.select_graph(GRAPH_NAME)

    # Count nodes by type
    node_types = ['Matter', 'Party', 'Clause', 'Recommendation', 'Decision', 'Concession']

    print("\nNode counts in cloud:")
    for node_type in node_types:
        result = cloud_graph.query(f'MATCH (n:{node_type}) RETURN COUNT(n) as count')
        count = result.result_set[0][0]
        print(f"  {node_type}: {count}")

    # Count relationships
    rel_types = ['HAS_RECOMMENDATION', 'HAS_DECISION', 'RESULTED_IN_CONCESSION']

    print("\nRelationship counts in cloud:")
    for rel_type in rel_types:
        result = cloud_graph.query(f'MATCH ()-[r:{rel_type}]->() RETURN COUNT(r) as count')
        count = result.result_set[0][0]
        print(f"  {rel_type}: {count}")

    print("\n✅ Verification complete!")


def main():
    """Main export process"""
    print("=" * 80)
    print("FALKORDB CLOUD EXPORT")
    print("Export local graph database to FalkorDB Cloud")
    print("=" * 80)

    # Check credentials
    check_cloud_credentials()

    # Connect to local
    local_db, local_graph = connect_to_local()

    # Connect to cloud
    cloud_db = connect_to_cloud()

    # Ask about clearing cloud data
    clear_cloud_graph(cloud_db)

    # Copy nodes
    nodes_copied = copy_nodes(local_graph, cloud_db)

    # Copy relationships
    rels_copied = copy_relationships(local_graph, cloud_db)

    # Verify
    verify_cloud_data(cloud_db)

    print("\n" + "=" * 80)
    print("✅ EXPORT COMPLETE!")
    print("=" * 80)
    print(f"\nYour graph is now available in FalkorDB Cloud:")
    print(f"  Host: {CLOUD_HOST}")
    print(f"  Graph: {GRAPH_NAME}")
    print(f"  Nodes: {nodes_copied}")
    print(f"  Relationships: {rels_copied}")
    print(f"\nAccess the graph browser at:")
    print(f"  https://{CLOUD_HOST}:3000")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Export cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
