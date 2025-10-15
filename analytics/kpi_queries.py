from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class QueryTemplate:
    name: str
    description: str
    cypher: str

    def with_parameters(self, **params: str) -> "Query":
        return Query(template=self, parameters=params)


@dataclass(frozen=True)
class Query:
    template: QueryTemplate
    parameters: Dict[str, str]

    @property
    def name(self) -> str:
        return self.template.name

    @property
    def cypher(self) -> str:
        return self.template.cypher

    @property
    def description(self) -> str:
        return self.template.description


def clause_lineage_template() -> QueryTemplate:
    return QueryTemplate(
        name="clause_lineage",
        description="Track clause lineage with associated decisions across versions.",
        cypher="""
MATCH path = (c1:Clause {canonical_clause_id:$canonical_clause_id})-[:EVOLVES_TO*0..]->(cN)
WITH nodes(path) AS clauses
UNWIND clauses AS clause
OPTIONAL MATCH (clause)-[:HAS_AGENT_RECOMMENDATION]->(rec)
OPTIONAL MATCH (rec)<-[:APPLIES_TO]-(decision)
RETURN clause.version_id AS version_id,
       clause.section_path AS section_path,
       rec.rec_id AS recommendation_id,
       decision.decision_type AS decision_type,
       decision.actor AS actor,
       decision.ts AS decided_at
ORDER BY clause.version_id;
""",
    )


def outstanding_recommendations_template() -> QueryTemplate:
    return QueryTemplate(
        name="outstanding_recommendations",
        description="Identify pending recommendations awaiting user action.",
        cypher="""
MATCH (rec:AgentRecommendation)
WHERE rec.status = 'pending'
  AND NOT EXISTS { MATCH (:UserDecision)-[:APPLIES_TO]->(rec) }
RETURN rec.rec_id AS recommendation_id,
       rec.issue_type AS issue_type,
       rec.severity AS severity,
       rec.ts AS created_at
ORDER BY rec.ts;
""",
    )


def handover_snapshot_template() -> QueryTemplate:
    return QueryTemplate(
        name="handover_snapshot",
        description="Gather session-specific context for a lawyer handover.",
        cypher="""
MATCH (session:ReviewSession {session_id:$session_id})
MATCH (session)<-[:LOGGED_IN]-(decision:UserDecision)-[:APPLIES_TO]->(rec:AgentRecommendation)
MATCH (rec)<-[:HAS_AGENT_RECOMMENDATION]-(clause:Clause)
OPTIONAL MATCH (rec)-[:JUSTIFIED_BY]->(rat:Rationale)
RETURN clause.section_path AS section_path,
       rec.issue_type AS issue_type,
       rec.severity AS severity,
       decision.decision_type AS decision_type,
       decision.status AS status,
       decision.actor AS actor,
       decision.ts AS decided_at,
       rat.rationale_text AS rationale
ORDER BY clause.section_path;
""",
    )


def concession_trail_template() -> QueryTemplate:
    return QueryTemplate(
        name="concession_trail",
        description="List recent concessions with timing and impact.",
        cypher="""
MATCH (cons:Concession)-[:AFFECTS_CLAUSE]->(clause:Clause)
WHERE cons.ts >= datetime($since)
RETURN clause.canonical_clause_id AS canonical_clause_id,
       clause.section_path AS section_path,
       cons.description AS description,
       cons.trigger AS trigger,
       cons.value_impact AS value_impact,
       cons.ts AS conceded_at
ORDER BY cons.ts DESC;
""",
    )


def default_templates() -> List[QueryTemplate]:
    return [
        clause_lineage_template(),
        outstanding_recommendations_template(),
        handover_snapshot_template(),
        concession_trail_template(),
    ]


def build_queries(params: Dict[str, str]) -> List[Query]:
    queries: List[Query] = []
    for template in default_templates():
        key_subset = {
            key: value
            for key, value in params.items()
            if key in template.cypher
        }
        queries.append(template.with_parameters(**key_subset))
    return queries


def describe_queries(queries: Iterable[Query]) -> List[Dict[str, str]]:
    payload: List[Dict[str, str]] = []
    for query in queries:
        payload.append(
            {
                "name": query.name,
                "description": query.description,
                "cypher": query.cypher.strip(),
                "parameters": query.parameters,
            }
        )
    return payload
