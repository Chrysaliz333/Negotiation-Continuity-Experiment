# Graphiti Analysis & Recommendations for Negotiation Continuity

## Executive Summary

Graphiti’s episodic, temporally-aware knowledge graph is a strong fit for tracking Leah’s recommendations, user responses, and concessions across multi-round negotiations. Its incremental ingestion, bi-temporal edges, and hybrid retrieval let us:

- Link clauses across versions with deterministic IDs.
- Record every agent suggestion plus associated rationale text.
- Capture user decisions (apply / override / custom edit) so Leah stops repeating resolved issues.
- Surface the history of concessions and when they occurred.

The existing MVE schema already covers documents, clauses, and basic decisions, but it lacks explicit modelling for recommendation lineage and concession tracking. The enhanced schema in `kg_schema_graphiti_enhanced.md` focuses on those gaps while staying lean.

---

## What Changes from the MVE Schema?

| Area | MVE | Graphiti-Enhanced |
| --- | --- | --- |
| **Recommendations** | Stored as text fields on clauses | Explicit `AgentRecommendation` + `SuggestedEdit` nodes with provenance |
| **User response** | Generic `Decision` node without link back to the recommendation | `UserDecision` with `decision_type` (apply/override/custom) tied to the recommendation |
| **Override suppression** | Not tracked | `UserDecision` edge marks overrides so Leah avoids resurfacing |
| **Concessions** | Not represented | Optional `Concession` node linked to decisions affecting business terms |
| **Temporal provenance** | Clause lineage only | Episodes attached to agent outputs and user actions |

---

## Implementation Outline

1. **Schema & Entities** (Day 1)
   - Define Pydantic models for `Document`, `DocVersion`, `Clause`, `AgentRecommendation`, `SuggestedEdit`, `Rationale`, `UserDecision`, `Concession`, `ReviewSession`, `Episode`.
   - Implement deterministic ID helpers (see schema doc).

2. **Ingestion Adapter** (Day 1-2)
   - Convert extractor output + Leah responses into Graphiti episodes.
   - For each clause change:
     1. Create/resolve `Clause` for the new version.
     2. Create `AgentRecommendation` + optional `SuggestedEdit` + `Rationale`.
     3. When the user responds, attach `UserDecision` (with `decision_type`).
     4. If it’s a give-up, create `Concession` and link.

3. **Queries & KPIs** (Day 3-4)
   - Implement Cypher queries from `kg_schema_graphiti_enhanced.md` for:
     - Clause linkage (lineage path)
     - Recommendation adherence (resolved vs outstanding)
     - Handover snapshot (review session context)
     - Concession trail (recent give-ups)
   - Store metrics in `data/metrics/graphiti_baseline.jsonl`.

4. **Optional Neptune Trial** (Day 5)
   - Deploy Graphiti with `graphiti-core[neptune]` to measure latency/cost at larger scale.

5. **Production Readiness** (Day 6-7)
   - Implement alert/warning when Leah attempts to reference a recommendation that already has `decision_type='OVERRIDE'`.
   - Build dashboards for outstanding recommendations and concession timelines.
   - Document runbooks (`PRODUCTION_INTEGRATION.md`).

---

## Key Graphiti Features to Leverage

- **Episodes**: Leah’s messages, user edits, and review sessions each become episodes; every node/edge links back for audit trails.
- **Bi-temporal edges**: Use `t_valid`/`t_invalid` to show when a clause state was true vs when we logged it.
- **Hybrid retrieval**: Combine embeddings and graph traversal to fetch the correct clause lineage plus decision history for a handover.
- **Custom entity types**: Pydantic-based schema keeps ingestion strict and discoverable.

---

## Example Pydantic Models

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict

class AgentRecommendation(BaseModel):
    rec_id: str
    clause_id: str
    issue_type: str
    severity: str
    suggested_action: str = Field(..., description="ACCEPT|EDIT|REMOVE")
    suggested_language: Optional[str]
    status: str = "pending"
    model_version: str
    ts: datetime

class UserDecision(BaseModel):
    decision_id: str
    rec_id: str
    clause_id: str
    decision_type: str = Field(..., description="APPLY_RECOMMENDATION|OVERRIDE|CUSTOM_EDIT|DEFER")
    status: str = "logged"
    actor: str
    ts: datetime
    notes: Optional[str]

class Concession(BaseModel):
    concession_id: str
    clause_id: str
    description: str
    trigger: str = Field(..., description="user_initiated|counterparty_pressure")
    value_impact: Optional[str]
    ts: datetime
```

---

## Sample Ingestion Flow

1. **Leah suggests an edit**
   - Create `Episode` (`agent_suggestion`).
   - Upsert `AgentRecommendation`, `SuggestedEdit`, `Rationale` linked to the clause and episode.
2. **User applies Leah’s suggestion**
   - Create `Episode` (`user_edit`).
   - Create `UserDecision` with `decision_type='APPLY_RECOMMENDATION'`, link to recommendation and clause.
3. **User overrides**
   - Set `decision_type='OVERRIDE'`.
   - Future recommendation generation checks for existing overrides before prompting.
4. **User concedes**
   - Create `Concession` node linked to the decision and clause.

---

## KPI Measurement Cheat Sheet

| KPI | Query | Notes |
| --- | --- | --- |
| Clause linkage | `EVOLVES_TO` path (schema query #2) | Expect >90% precision, >85% recall |
| Recommendation adherence | Outstanding vs resolved recommendations (queries #1 & #5) | Tracks Leah success rate |
| Handover reliability | Review session snapshot (query #4) | Ensures new lawyer sees full context |
| Concession tracking | Recent concessions (query #3) | Measures negotiation give-ups |

---

## Risks & Mitigations

| Risk | Mitigation |
| --- | --- |
| Incomplete recorder of overrides | Enforce ingestion rule: any user change touching a clause must log a `UserDecision` |
| Duplicate recommendations | Canonical recommendation ID = sha(clause + issue_type + ts bucket) |
| Leah re-raising resolved issues | Agent runtime checks for existing `decision_type='OVERRIDE'` before prompting |
| Missing concessions | UI/agent prompt users to tag decision as concession when applicable |

---

## Next Steps

1. Implement the enhanced schema and ingestion adapter (Day 1-2).
2. Populate the graph with at least one end-to-end negotiation to validate lineage queries.
3. Execute KPI queries and log metrics (Day 3-4).
4. Optionally trial Neptune (Day 5) and prepare production readiness tasks (Day 6-7).

With this lineage-focused schema, the graph becomes the single source of truth for what Leah asked, what users did, and which concessions were made—setting the stage for smarter, context-aware negotiation agents.
