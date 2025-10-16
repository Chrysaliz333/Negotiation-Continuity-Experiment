#!/usr/bin/env python3
"""
Export local FalkorDB graph to Cypher file for manual cloud import

Usage:
    python3 scripts/export_to_cypher_file.py > export/negotiation_continuity.cypher
"""

from falkordb import FalkorDB

def export_to_cypher():
    """Export graph as Cypher CREATE statements"""

    # Connect to local FalkorDB
    db = FalkorDB(host='localhost', port=6379)
    graph = db.select_graph('negotiation_continuity')

    print("// Negotiation Continuity Knowledge Graph")
    print("// Export for FalkorDB Cloud Import")
    print("// " + "="*70)
    print()

    # Export nodes by type
    node_types = ['Matter', 'Party', 'Clause', 'Recommendation', 'Decision', 'Concession']

    for node_type in node_types:
        print(f"// {node_type} Nodes")
        print("// " + "-"*70)

        result = graph.query(f'MATCH (n:{node_type}) RETURN n')

        for row in result.result_set:
            node = row[0]
            props = node.properties

            # Build property string
            prop_parts = []
            for key, value in props.items():
                if isinstance(value, str):
                    # Escape special characters
                    value = value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
                    prop_parts.append(f'{key}: "{value}"')
                elif isinstance(value, bool):
                    prop_parts.append(f'{key}: {str(value).lower()}')
                elif value is not None:
                    prop_parts.append(f'{key}: {value}')

            props_str = ', '.join(prop_parts)
            print(f'CREATE (:{node_type} {{{props_str}}})')

        print()

    # Export relationships
    print("// Relationships")
    print("// " + "-"*70)

    rel_types = ['HAS_RECOMMENDATION', 'HAS_DECISION', 'RESULTED_IN_CONCESSION']

    for rel_type in rel_types:
        result = graph.query(f'''
            MATCH (a)-[:{rel_type}]->(b)
            RETURN labels(a)[0] as from_type,
                   a as from_node,
                   labels(b)[0] as to_type,
                   b as to_node
        ''')

        for row in result.result_set:
            from_type = row[0]
            from_node = row[1]
            to_type = row[2]
            to_node = row[3]

            # Get ID properties
            from_id = get_id_match(from_type, from_node.properties)
            to_id = get_id_match(to_type, to_node.properties)

            print(f'MATCH (a:{from_type} {{{from_id}}}), (b:{to_type} {{{to_id}}})')
            print(f'CREATE (a)-[:{rel_type}]->(b)')

        print()

    print("// Export Complete - " + str(result.result_set[0] if result.result_set else 0) + " relationships")

def get_id_match(node_type, properties):
    """Get ID property match string for a node"""
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

    # Escape value
    id_value = id_value.replace('\\', '\\\\').replace('"', '\\"')

    return f'{id_field}: "{id_value}"'

if __name__ == "__main__":
    export_to_cypher()
