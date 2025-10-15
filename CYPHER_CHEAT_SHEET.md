# Cypher Query Cheat Sheet - Negotiation Continuity System

**Quick reference for querying the knowledge graph**

---

## 📋 Table of Contents

1. [Basic Patterns](#basic-patterns)
2. [Node Types](#node-types)
3. [Relationships](#relationships)
4. [Common Queries](#common-queries)
5. [Filtering](#filtering)
6. [Aggregation](#aggregation)
7. [Useful Examples](#useful-examples)
8. [Advanced Queries](#advanced-queries)

---

## 1. Basic Patterns

### Match All Nodes
```cypher
MATCH (n)
RETURN n
LIMIT 10
```

### Match Nodes by Label
```cypher
MATCH (c:Clause)
RETURN c
LIMIT 10
```

### Match Nodes by Property
```cypher
MATCH (c:Clause {matter_id: 'matter_001'})
RETURN c
```

### Match with Multiple Properties
```cypher
MATCH (c:Clause {matter_id: 'matter_001', version: 1})
RETURN c
```

### Count Nodes
```cypher
MATCH (n)
RETURN COUNT(n) as total_nodes
```

### Count by Type
```cypher
MATCH (n)
RETURN labels(n)[0] as type, COUNT(n) as count
ORDER BY count DESC
```

---

## 2. Node Types

### Your System Has 6 Node Types:

```cypher
// 1. Matter
MATCH (m:Matter)
RETURN m.matter_id, m.version, m.matter_type
LIMIT 5

// 2. Party
MATCH (p:Party)
RETURN p.name, p.role, p.matter_id
LIMIT 5

// 3. Clause
MATCH (c:Clause)
RETURN c.clause_number, c.title, c.category, c.version
LIMIT 5

// 4. Recommendation
MATCH (r:Recommendation)
RETURN r.issue_type, r.classification, r.reasoning
LIMIT 5

// 5. Decision
MATCH (d:Decision)
RETURN d.decision_type, d.actor, d.role, d.timestamp
LIMIT 5

// 6. Concession
MATCH (con:Concession)
RETURN con.description, con.impact, con.rationale
LIMIT 5
```

---

## 3. Relationships

### Your System Has 3 Relationship Types:

```cypher
// 1. HAS_RECOMMENDATION: Clause → Recommendation
MATCH (c:Clause)-[:HAS_RECOMMENDATION]->(r:Recommendation)
RETURN c.title, r.issue_type
LIMIT 5

// 2. HAS_DECISION: Recommendation → Decision
MATCH (r:Recommendation)-[:HAS_DECISION]->(d:Decision)
RETURN r.issue_type, d.decision_type, d.actor
LIMIT 5

// 3. RESULTED_IN_CONCESSION: Decision → Concession
MATCH (d:Decision)-[:RESULTED_IN_CONCESSION]->(con:Concession)
RETURN d.actor, con.description, con.impact
LIMIT 5
```

### Find All Relationships
```cypher
MATCH (a)-[r]->(b)
RETURN labels(a)[0] as from,
       type(r) as relationship,
       labels(b)[0] as to,
       COUNT(*) as count
```

---

## 4. Common Queries

### Find a Specific Matter
```cypher
MATCH (m:Matter {matter_id: 'matter_001', version: 1})
RETURN m
```

### Get All Versions of a Matter
```cypher
MATCH (m:Matter {matter_id: 'matter_001'})
RETURN m.version, m.timestamp
ORDER BY m.version
```

### Find a Specific Clause
```cypher
MATCH (c:Clause {matter_id: 'matter_001', clause_number: '1.1'})
RETURN c.version, c.title, c.category
ORDER BY c.version
```

### Get Clauses for a Version
```cypher
MATCH (c:Clause {matter_id: 'matter_001', version: 1})
RETURN c.clause_number, c.title, c.category
ORDER BY c.clause_number
```

### Find Recommendations for a Clause
```cypher
MATCH (c:Clause {clause_id: 'clause_1826c7c4f76e928f'})
MATCH (c)-[:HAS_RECOMMENDATION]->(r:Recommendation)
RETURN c.clause_number, r.issue_type, r.classification
```

### Find Decisions by Actor
```cypher
MATCH (d:Decision {actor: 'Jessica Martinez'})
RETURN d.matter_id, d.decision_type, d.timestamp, d.notes
ORDER BY d.timestamp
```

### Find All Concessions
```cypher
MATCH (d:Decision)-[:RESULTED_IN_CONCESSION]->(con:Concession)
RETURN con.matter_id, d.actor, con.description, con.impact
```

---

## 5. Filtering

### WHERE Clause
```cypher
MATCH (c:Clause)
WHERE c.version = 1
RETURN c.title, c.category
LIMIT 10
```

### Multiple Conditions (AND)
```cypher
MATCH (c:Clause)
WHERE c.matter_id = 'matter_001' AND c.version = 1
RETURN c.clause_number, c.title
```

### Multiple Conditions (OR)
```cypher
MATCH (c:Clause)
WHERE c.version = 1 OR c.version = 2
RETURN c.matter_id, c.version, c.title
LIMIT 10
```

### String Matching (CONTAINS)
```cypher
MATCH (c:Clause)
WHERE c.title CONTAINS 'Liability'
RETURN c.matter_id, c.clause_number, c.title
```

### Case-Insensitive Search
```cypher
MATCH (c:Clause)
WHERE toLower(c.title) CONTAINS toLower('liability')
RETURN c.title
```

### Range Queries
```cypher
MATCH (c:Clause)
WHERE c.version >= 2 AND c.version <= 4
RETURN c.matter_id, c.version, c.title
```

### NOT Condition
```cypher
MATCH (r:Recommendation)
WHERE NOT r.classification = 'favorable'
RETURN r.issue_type, r.classification
LIMIT 10
```

### IN List
```cypher
MATCH (c:Clause)
WHERE c.category IN ['Liability and Risk', 'Data Protection']
RETURN c.title, c.category
LIMIT 10
```

---

## 6. Aggregation

### COUNT
```cypher
MATCH (c:Clause)
RETURN COUNT(c) as total_clauses
```

### COUNT by Group
```cypher
MATCH (c:Clause)
RETURN c.category, COUNT(c) as count
ORDER BY count DESC
```

### COUNT DISTINCT
```cypher
MATCH (c:Clause)
RETURN COUNT(DISTINCT c.matter_id) as total_matters
```

### SUM, AVG, MIN, MAX
```cypher
MATCH (m:Matter)
RETURN COUNT(DISTINCT m.matter_id) as matters,
       MIN(m.version) as min_version,
       MAX(m.version) as max_version
```

### COLLECT (Create Lists)
```cypher
MATCH (c:Clause {matter_id: 'matter_001', version: 1})
RETURN COLLECT(c.title) as all_titles
```

---

## 7. Useful Examples

### Cross-Version Clause Tracking
```cypher
MATCH (c:Clause {matter_id: 'matter_001', clause_number: '1.1'})
OPTIONAL MATCH (c)-[:HAS_RECOMMENDATION]->(r:Recommendation)
OPTIONAL MATCH (r)-[:HAS_DECISION]->(d:Decision)
RETURN c.version,
       c.title,
       r.classification,
       r.issue_type,
       d.decision_type,
       d.actor
ORDER BY c.version
```

### Unfavorable Recommendations
```cypher
MATCH (c:Clause)-[:HAS_RECOMMENDATION]->(r:Recommendation {classification: 'unfavorable'})
OPTIONAL MATCH (r)-[:HAS_DECISION]->(d:Decision)
RETURN c.matter_id,
       c.version,
       c.clause_number,
       c.title,
       r.issue_type,
       d.decision_type,
       d.actor
ORDER BY c.matter_id, c.version
LIMIT 20
```

### Recommendation Coverage by Version
```cypher
MATCH (m:Matter {matter_id: 'matter_001'})
OPTIONAL MATCH (c:Clause {matter_id: 'matter_001', version: m.version})
OPTIONAL MATCH (c)-[:HAS_RECOMMENDATION]->(r:Recommendation)
RETURN m.version,
       COUNT(DISTINCT c) as total_clauses,
       COUNT(DISTINCT r) as recommendations,
       ROUND(100.0 * COUNT(DISTINCT r) / COUNT(DISTINCT c)) as coverage_percent
ORDER BY m.version
```

### Override Decisions (Potential Concessions)
```cypher
MATCH (r:Recommendation {classification: 'unfavorable'})-[:HAS_DECISION]->(d:Decision {decision_type: 'override'})
MATCH (c:Clause)-[:HAS_RECOMMENDATION]->(r)
OPTIONAL MATCH (d)-[:RESULTED_IN_CONCESSION]->(con:Concession)
RETURN c.matter_id,
       c.clause_number,
       c.title,
       r.issue_type,
       d.actor,
       d.notes,
       con.description
```

### Decision Type Distribution
```cypher
MATCH (d:Decision)
WITH COUNT(d) as total
MATCH (d2:Decision)
RETURN d2.decision_type,
       COUNT(d2) as count,
       ROUND(100.0 * COUNT(d2) / total) as percentage
ORDER BY count DESC
```

### Clauses by Category
```cypher
MATCH (c:Clause)
RETURN c.category, COUNT(c) as count
ORDER BY count DESC
```

### Complete Chain for a Clause
```cypher
MATCH (c:Clause {matter_id: 'matter_001', version: 1, clause_number: '1.1'})
OPTIONAL MATCH (c)-[:HAS_RECOMMENDATION]->(r:Recommendation)
OPTIONAL MATCH (r)-[:HAS_DECISION]->(d:Decision)
OPTIONAL MATCH (d)-[:RESULTED_IN_CONCESSION]->(con:Concession)
RETURN c.clause_id,
       c.title,
       r.recommendation_id,
       r.issue_type,
       r.classification,
       d.decision_id,
       d.decision_type,
       d.actor,
       con.concession_id,
       con.description
```

### Find Clauses Without Recommendations
```cypher
MATCH (c:Clause)
WHERE NOT (c)-[:HAS_RECOMMENDATION]->(:Recommendation)
RETURN c.matter_id, c.version, c.clause_number, c.title
LIMIT 10
```

### Find Recommendations Without Decisions
```cypher
MATCH (r:Recommendation)
WHERE NOT (r)-[:HAS_DECISION]->(:Decision)
MATCH (c:Clause)-[:HAS_RECOMMENDATION]->(r)
RETURN c.matter_id, c.clause_number, r.issue_type, r.classification
LIMIT 10
```

---

## 8. Advanced Queries

### Path Queries (Find All Paths)
```cypher
MATCH path = (c:Clause)-[:HAS_RECOMMENDATION]->()-[:HAS_DECISION]->()-[:RESULTED_IN_CONCESSION]->()
WHERE c.matter_id = 'matter_001'
RETURN path
LIMIT 5
```

### Variable Length Paths
```cypher
MATCH path = (c:Clause)-[*1..3]->(other)
WHERE c.clause_id = 'clause_1826c7c4f76e928f'
RETURN path
LIMIT 10
```

### Shortest Path
```cypher
MATCH (c:Clause {clause_id: 'clause_1826c7c4f76e928f'}),
      (con:Concession {concession_id: 'con_5cb3d89dd4d88ab7'})
MATCH path = shortestPath((c)-[*]-(con))
RETURN path
```

### Subqueries with WITH
```cypher
MATCH (c:Clause {matter_id: 'matter_001'})
WITH c, COUNT(c) as clause_count
WHERE clause_count > 0
MATCH (c)-[:HAS_RECOMMENDATION]->(r:Recommendation)
RETURN c.version, clause_count, COUNT(r) as rec_count
ORDER BY c.version
```

### UNION (Combine Results)
```cypher
MATCH (c:Clause {category: 'Liability and Risk'})
RETURN c.title as title, 'Liability' as type
UNION
MATCH (c:Clause {category: 'Data Protection'})
RETURN c.title as title, 'Data Protection' as type
```

### Pattern Comprehension
```cypher
MATCH (c:Clause {matter_id: 'matter_001', version: 1})
RETURN c.clause_number,
       c.title,
       [(c)-[:HAS_RECOMMENDATION]->(r) | r.issue_type] as issues
```

---

## 9. Sorting & Limiting

### ORDER BY
```cypher
MATCH (c:Clause)
RETURN c.matter_id, c.version, c.clause_number, c.title
ORDER BY c.matter_id, c.version, c.clause_number
LIMIT 10
```

### ORDER BY DESC
```cypher
MATCH (d:Decision)
RETURN d.actor, d.timestamp, d.decision_type
ORDER BY d.timestamp DESC
LIMIT 10
```

### SKIP and LIMIT (Pagination)
```cypher
MATCH (c:Clause)
RETURN c.title
ORDER BY c.title
SKIP 10
LIMIT 10
```

---

## 10. Updating Data (Use with Caution)

### Create a Node
```cypher
CREATE (c:Clause {
    clause_id: 'new_clause_123',
    clause_number: '11.11',
    title: 'New Clause',
    version: 5,
    matter_id: 'matter_001'
})
RETURN c
```

### Create a Relationship
```cypher
MATCH (c:Clause {clause_id: 'clause_123'}),
      (r:Recommendation {recommendation_id: 'rec_456'})
CREATE (c)-[:HAS_RECOMMENDATION]->(r)
```

### Update Properties
```cypher
MATCH (c:Clause {clause_id: 'clause_123'})
SET c.title = 'Updated Title'
RETURN c
```

### Delete a Node (and its relationships)
```cypher
MATCH (c:Clause {clause_id: 'clause_123'})
DETACH DELETE c
```

---

## 11. Useful Functions

### String Functions
```cypher
MATCH (c:Clause)
RETURN c.title,
       toLower(c.title) as lowercase,
       toUpper(c.title) as uppercase,
       substring(c.title, 0, 10) as first_10_chars,
       replace(c.title, 'Liability', 'Risk') as replaced
LIMIT 5
```

### List Functions
```cypher
MATCH (c:Clause {matter_id: 'matter_001', version: 1})
WITH COLLECT(c.title) as titles
RETURN titles,
       size(titles) as count,
       head(titles) as first,
       last(titles) as last
```

### Date/Time (if timestamps are used)
```cypher
MATCH (d:Decision)
RETURN d.timestamp,
       substring(d.timestamp, 0, 10) as date_only
LIMIT 5
```

### CASE (Conditional Logic)
```cypher
MATCH (r:Recommendation)
RETURN r.classification,
       CASE r.classification
         WHEN 'unfavorable' THEN 'High Priority'
         WHEN 'requires_clarification' THEN 'Medium Priority'
         ELSE 'Low Priority'
       END as priority
LIMIT 10
```

---

## 12. Performance Tips

### Use LIMIT for Exploration
```cypher
// Good for testing
MATCH (n)
RETURN n
LIMIT 10
```

### Use Indexes (Check with Admin)
```cypher
// Create index (admin only)
CREATE INDEX ON :Clause(clause_number)

// Create index on multiple properties
CREATE INDEX ON :Clause(matter_id, version)
```

### Use EXPLAIN to See Query Plan
```cypher
EXPLAIN
MATCH (c:Clause {matter_id: 'matter_001'})
RETURN c
```

### Use PROFILE for Performance Analysis
```cypher
PROFILE
MATCH (c:Clause)-[:HAS_RECOMMENDATION]->(r:Recommendation)
RETURN c.title, COUNT(r)
```

---

## 13. Quick Reference Card

### Basic Pattern: `MATCH ... RETURN ... LIMIT`
```cypher
MATCH (n:Label {property: 'value'})
RETURN n
LIMIT 10
```

### With Relationships: `MATCH ... -[rel]-> ... RETURN`
```cypher
MATCH (a:Label1)-[:REL_TYPE]->(b:Label2)
RETURN a, b
LIMIT 10
```

### With Filtering: `MATCH ... WHERE ... RETURN`
```cypher
MATCH (n:Label)
WHERE n.property > 10
RETURN n
```

### With Aggregation: `MATCH ... RETURN ... GROUP BY`
```cypher
MATCH (n:Label)
RETURN n.category, COUNT(n) as count
ORDER BY count DESC
```

---

## 14. Your System's Key Queries

### 1. Get All Matters
```cypher
MATCH (m:Matter)
RETURN DISTINCT m.matter_id, m.matter_type
ORDER BY m.matter_id
```

### 2. Track Clause Across Versions
```cypher
MATCH (c:Clause {matter_id: 'matter_001', clause_number: '1.1'})
RETURN c.version, c.title
ORDER BY c.version
```

### 3. Find All Concessions
```cypher
MATCH (d:Decision)-[:RESULTED_IN_CONCESSION]->(con:Concession)
MATCH (c:Clause {clause_id: con.clause_id})
RETURN con.matter_id, c.clause_number, c.title,
       d.actor, con.description, con.impact
ORDER BY d.timestamp
```

### 4. Decisions by Actor
```cypher
MATCH (d:Decision {actor: 'Jessica Martinez'})
MATCH (r:Recommendation)-[:HAS_DECISION]->(d)
MATCH (c:Clause)-[:HAS_RECOMMENDATION]->(r)
RETURN c.matter_id, c.clause_number, c.title,
       r.classification, d.decision_type, d.timestamp
ORDER BY d.timestamp
```

### 5. Version Comparison
```cypher
MATCH (c1:Clause {matter_id: 'matter_001', version: 1, clause_number: '1.1'}),
      (c2:Clause {matter_id: 'matter_001', version: 2, clause_number: '1.1'})
OPTIONAL MATCH (c1)-[:HAS_RECOMMENDATION]->(r1:Recommendation)
OPTIONAL MATCH (c2)-[:HAS_RECOMMENDATION]->(r2:Recommendation)
RETURN c1.version as v1,
       COUNT(r1) as v1_recs,
       c2.version as v2,
       COUNT(r2) as v2_recs
```

---

## 15. Running Queries

### From Python
```python
from falkordb import FalkorDB

db = FalkorDB(host='localhost', port=6379)
graph = db.select_graph('negotiation_continuity')

result = graph.query('''
    MATCH (c:Clause {matter_id: 'matter_001'})
    RETURN c.clause_number, c.title
    LIMIT 5
''')

for row in result.result_set:
    print(f"Clause {row[0]}: {row[1]}")
```

### From Browser (FalkorDB UI)
1. Open: http://localhost:3000
2. Click "Connect"
3. Select graph: `negotiation_continuity`
4. Enter query in the query box
5. Click "Run"

### From Command Line
```bash
docker exec falkordb redis-cli GRAPH.QUERY negotiation_continuity "MATCH (n) RETURN COUNT(n)"
```

---

## 📚 Additional Resources

### Official Cypher Documentation
- Neo4j Cypher Manual: https://neo4j.com/docs/cypher-manual/
- FalkorDB Docs: https://docs.falkordb.com/

### Quick Tips
- Use `LIMIT` when exploring to avoid large result sets
- Use `EXPLAIN` to understand query performance
- Start simple, add complexity gradually
- Test on small subsets before running on full data

---

## 🎯 Practice Queries

Try these to learn:

```cypher
-- 1. Count everything
MATCH (n) RETURN labels(n)[0] as type, COUNT(n) ORDER BY COUNT(n) DESC

-- 2. Sample of each node type
MATCH (n) RETURN labels(n)[0] as type, n LIMIT 3

-- 3. All relationships
MATCH (a)-[r]->(b) RETURN type(r), COUNT(*) ORDER BY COUNT(*) DESC

-- 4. Find a specific clause
MATCH (c:Clause {clause_number: '1.1'}) RETURN c LIMIT 5

-- 5. Complete chain example
MATCH (c:Clause {matter_id: 'matter_001', version: 1})
MATCH (c)-[:HAS_RECOMMENDATION]->(r)-[:HAS_DECISION]->(d)
RETURN c.title, r.issue_type, d.decision_type LIMIT 5
```

---

**Happy Querying!** 🚀

For more help: See `QUICK_START.md` or run `python3 scripts/nl_query.py` and type `help`
