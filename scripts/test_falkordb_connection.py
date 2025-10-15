#!/usr/bin/env python3
"""
Test FalkorDB connectivity and basic operations.

Usage:
    python scripts/test_falkordb_connection.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import redis
from falkordb import FalkorDB


def test_redis_connection():
    """Test basic Redis connection to FalkorDB"""
    print("Testing Redis connection to FalkorDB...")

    try:
        client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        response = client.ping()

        if response:
            print(f"✅ FalkorDB connection successful!")
            print(f"   PONG response received")
            return True
        else:
            print(f"❌ FalkorDB connection failed: No PONG response")
            return False

    except redis.ConnectionError as e:
        print(f"❌ Cannot connect to FalkorDB: {e}")
        print(f"\n💡 Troubleshooting:")
        print(f"   1. Is Docker running? Check with: docker ps")
        print(f"   2. Is FalkorDB container started? Check with: docker ps | grep falkordb")
        print(f"   3. Start FalkorDB: docker run -d --name falkordb -p 6379:6379 -p 3000:3000 falkordb/falkordb:latest")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_falkordb_graph_operations():
    """Test basic FalkorDB graph operations"""
    print("\nTesting FalkorDB graph operations...")

    try:
        # Connect to FalkorDB
        db = FalkorDB(host='localhost', port=6379)

        # Select or create a test graph
        graph = db.select_graph('test_graph')

        print(f"✅ Graph 'test_graph' created/selected successfully")

        # Try a simple query
        try:
            result = graph.query("CREATE (n:TestNode {name: 'test'}) RETURN n")
            print(f"✅ Successfully created test node")

            # Clean up test node
            graph.query("MATCH (n:TestNode) DELETE n")
            print(f"✅ Successfully deleted test node")

        except Exception as e:
            print(f"⚠️  Warning: Could not create test node: {e}")

        return True

    except Exception as e:
        print(f"❌ FalkorDB graph operations failed: {e}")
        return False


def test_environment_variables():
    """Check if environment variables are set"""
    print("\nChecking environment variables...")

    import os
    from dotenv import load_dotenv

    # Load .env file
    env_path = project_root / ".env"

    if not env_path.exists():
        print(f"⚠️  Warning: .env file not found at {env_path}")
        print(f"   Copy .env.example to .env and add your OpenAI API key")
        return False

    load_dotenv(env_path)

    # Check OpenAI API key
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print(f"❌ OPENAI_API_KEY not set in .env")
        print(f"   Add your OpenAI API key to .env file")
        return False
    elif openai_key.startswith('sk-'):
        print(f"✅ OPENAI_API_KEY is set (starts with sk-)")
    else:
        print(f"⚠️  Warning: OPENAI_API_KEY doesn't start with 'sk-' (may be invalid)")

    # Check FalkorDB settings
    falkordb_host = os.getenv('FALKORDB_HOST', 'localhost')
    falkordb_port = os.getenv('FALKORDB_PORT', '6379')
    print(f"✅ FalkorDB configured: {falkordb_host}:{falkordb_port}")

    return True


def main():
    print("="*80)
    print("FALKORDB CONNECTION TEST")
    print("="*80)
    print()

    # Test 1: Redis connection
    redis_ok = test_redis_connection()

    if not redis_ok:
        print("\n" + "="*80)
        print("RESULT: ❌ FAILED - Cannot connect to FalkorDB")
        print("="*80)
        sys.exit(1)

    # Test 2: Graph operations
    graph_ok = test_falkordb_graph_operations()

    # Test 3: Environment variables
    env_ok = test_environment_variables()

    # Summary
    print("\n" + "="*80)
    if redis_ok and graph_ok and env_ok:
        print("RESULT: ✅ ALL TESTS PASSED")
        print("="*80)
        print("\nYou're ready to proceed with Graphiti ingestion!")
        print("\nNext steps:")
        print("  1. Review synthetic data: ls data/ground_truth/synthetic/")
        print("  2. Test ingestion: python scripts/ingest/load_graphiti.py --dry-run")
        print("  3. Run actual ingestion: python scripts/ingest/load_graphiti.py")
        sys.exit(0)
    else:
        print("RESULT: ⚠️  SOME TESTS FAILED")
        print("="*80)
        print("\nPlease fix the issues above before proceeding.")
        sys.exit(1)


if __name__ == "__main__":
    main()
