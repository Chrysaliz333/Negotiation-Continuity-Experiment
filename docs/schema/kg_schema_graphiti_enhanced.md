# Contract Review KG Schema (Graphiti Continuity Focus)

## Design Principles

1. **User-centric lineage** – capture every recommendation from Leah, user response, and resulting clause state.
2. **Stop-repeat guardrails** – once a user overrides a recommendation, record it so the agent does not resurface the issue.
3. **Concession visibility** – track negotiated give-ups and when they occurred.
4. **Bi-temporal metadata** – preserve when an event happened in the negotiation and when it was logged.
5. **Episode provenance** – every fact is tied back to the episode (message, review session, upload) that produced it.

---

## Entities (Nodes)

### Document Management
- **Document**: `doc_id`, `title`, `counterparty`, `matter_id`, `document_type`, `jurisdiction`, `created_at`
- **DocVersion**: `version_id`, `version_no`, `source` (customer/counterparty/agent), `ts`, `hash`, `state`, `negotiation_round`
- **ReviewSession**: `session_id`, `actor`, `ts_started`, `ts_completed`, `summary`

### Clause & Content
- **Clause**: `clause_id`, `canonical_clause_id`, `section_path`, `clause_type`, `clause_name`, `text`, `text_hash`, `start_char`, `end_char`, `page`, `word_count`, `risk_level`, `position_score`, `version_id`
  - Optional enrichments: `tags` (array of playbook categories), `playbook_flags` (object of structured attributes)
- **ClauseSnapshot** (optional): raw clause text archived per version if you want to keep immutable copies.

### Agent Output & User Actions
- **AgentRecommendation**: `rec_id`, `issue_type`, `severity`, `suggested_action` (`ACCEPT`/`EDIT`/`REMOVE`), `suggested_language`, `ts`, `model_version`
- **SuggestedEdit**: `edit_id`, `op` (`insert`/`replace`/`delete`), `payload_json`, `proposed_by` (Leah), `proposed_at`
- **Rationale**: `rationale_id`, `rationale_text`, `json_blob`, `reasoning_type` (`risk_based`/`precedent_based`/`strategy`), `confidence`, `ts`
- **UserDecision**: `decision_id`, `decision_type` (`APPLY_RECOMMENDATION`/`OVERRIDE`/`DEFER`/`CUSTOM_EDIT`), `status` (`logged`/`implemented`/`superseded`), `actor`, `ts`, `notes`
- **Concession**: `concession_id`, `description`, `trigger` (`user_initiated`/`counterparty_pressure`), `value_impact`, `ts`

### Temporal & Provenance
- **Episode**: `episode_id`, `episode_type` (`negotiation_round`/`user_edit`/`agent_suggestion`), `reference_time`, `ingestion_time`, `actor`, `tool_version`, `checksum`, `metadata`
- **Party**: `party_id`, `name`, `role` (`customer`/`vendor`/`internal`)

_All nodes carry standard created/updated timestamps when convenient._

---

## Relationships (Edges)

Each edge includes `t_created`, `t_expired`, `t_valid`, `t_invalid`, `confidence`, `source_episode_id`.

- `(Document)-[:HAS_VERSION]->(DocVersion)` / `(DocVersion)-[:OF_DOCUMENT]->(Document)`
- `(DocVersion)-[:REVIEWED_IN]->(ReviewSession)`
- `(Clause)-[:BELONGS_TO]->(DocVersion)`
- `(Clause)-[:EVOLVES_TO {method, confidence, session_id}]->(Clause)` – lineage across versions
- `(Clause)-[:HAS_AGENT_RECOMMENDATION]->(AgentRecommendation)`
- `(AgentRecommendation)-[:HAS_EDIT]->(SuggestedEdit)`
- `(AgentRecommendation)-[:JUSTIFIED_BY]->(Rationale)`
- `(AgentRecommendation)-[:RECORDED_IN]->(ReviewSession)`
- `(UserDecision)-[:APPLIES_TO]->(AgentRecommendation)`
- `(UserDecision)-[:RESULTS_IN]->(Clause)` – pointer to the clause state after the decision
- `(UserDecision)-[:LOGGED_IN]->(ReviewSession)`
- `(UserDecision)-[:TRIGGERS_CONCESSION]->(Concession)` *(optional, only when decision yields a give-up)*
- `(Concession)-[:AFFECTS_CLAUSE]->(Clause)`
- `(SuggestedEdit)-[:TARGETS_CLAUSE]->(Clause)`
- `(Episode)-[:MATERIALIZES]->(AgentRecommendation|UserDecision|SuggestedEdit|Clause)`
- `(Party)-[:PART_OF]->(Document)` / `(ReviewSession)-[:ATTENDED_BY]->(Party)`

### Derived Helper Views
- **Resolved Recommendation**: `AgentRecommendation` with a `UserDecision` edge.
- **Outstanding Recommendation**: `AgentRecommendation` with no `UserDecision` and active (`status = pending`).
- **Suppressed Topic**: `AgentRecommendation` with `UserDecision.decision_type = 'OVERRIDE'`; Leah should avoid repeating.
- **Concession Trail**: Path `Clause` → `UserDecision` → `Concession` (ordered by time).

---

## Identity Rules

- `doc_id = sha256(matter_id | normalized_title)`
- `version_id = sha256(doc_id | file_name | uploader | ts)`
- `clause_id = sha256(version_id | section_path | start_char | end_char | text_hash)`
- `canonical_clause_id = sha256(matter_id | clause_type | section_path)`
- `rec_id = uuid4()` (or derived from clause + timestamp if you need deterministic IDs)
- `decision_id = sha256(rec_id | actor | ts)`
- `concession_id = uuid4()`
- `episode_id = uuid4()`

---

## Example Queries

### 1. Find Overridden Recommendations (so Leah stops re-raising)
```cypher
MATCH (c:Clause {canonical_clause_id:$canonical})-[:HAS_AGENT_RECOMMENDATION]->(rec)
MATCH (rec)<-[:APPLIES_TO]-(decision:UserDecision {decision_type:'OVERRIDE'})
RETURN rec.rec_id AS recommendation,
       decision.actor AS resolved_by,
       decision.ts AS decided_at,
       decision.notes AS notes
ORDER BY decision.ts DESC
LIMIT 5;
```

### 2. Show Clause Lineage With Decisions
```cypher
MATCH path = (c1:Clause {version_id:$v1})-[:EVOLVES_TO*0..]->(cN:Clause {version_id:$vN})
WITH nodes(path) AS clauses
UNWIND clauses AS clause
OPTIONAL MATCH (clause)-[:HAS_AGENT_RECOMMENDATION]->(rec)
OPTIONAL MATCH (rec)<-[:APPLIES_TO]-(decision)
RETURN clause.version_id,
       clause.section_path,
       rec.rec_id,
       decision.decision_type,
       decision.actor,
       decision.ts
ORDER BY clause.version_id;
```

### 3. List Active Concessions
```cypher
MATCH (cons:Concession)-[:AFFECTS_CLAUSE]->(clause)
WHERE cons.ts >= datetime($since)
RETURN clause.section_path,
       clause.version_id,
       cons.description,
       cons.value_impact,
       cons.ts
ORDER BY cons.ts DESC;
```

### 4. Handover Snapshot for a Session
```cypher
MATCH (session:ReviewSession {session_id:$session})
MATCH (session)<-[:LOGGED_IN]-(decision:UserDecision)-[:APPLIES_TO]->(rec:AgentRecommendation)
MATCH (rec)<-[:HAS_AGENT_RECOMMENDATION]-(clause:Clause)
OPTIONAL MATCH (rec)-[:JUSTIFIED_BY]->(rat:Rationale)
RETURN clause.section_path,
       rec.issue_type,
       rec.severity,
       decision.decision_type,
       decision.status,
       decision.actor,
       decision.ts,
       rat.rationale_text
ORDER BY clause.section_path;
```

### 5. Detect Recommendations Awaiting User Action
```cypher
MATCH (rec:AgentRecommendation)
WHERE rec.status = 'pending'
  AND NOT EXISTS { MATCH (:UserDecision)-[:APPLIES_TO]->(rec) }
RETURN rec.rec_id,
       rec.issue_type,
       rec.severity,
       rec.ts
ORDER BY rec.ts;
```

---

## Implementation Notes

- **Bi-temporal fields**: Use Graphiti’s episodic ingestion to populate `t_valid`/`t_invalid`. When a clause evolves, expire the previous `BELONGS_TO` edge and record the new one.
- **Override suppression**: Persist a flag on `UserDecision` (`decision_type='OVERRIDE'`). Downstream agent logic should query for existing overrides before recommending again.
- **Concession tagging**: Not every decision needs a concession. Use the relationship only when the user explicitly trades something away.
- **Review sessions**: Treat each lawyer/agent touchpoint as a `ReviewSession` so you can reconstruct the storyline quickly.
- **Episodes**: Leah’s outputs (`AgentRecommendation`, `SuggestedEdit`, `Rationale`) and user responses (`UserDecision`, `Concession`) should each reference the episode that generated them. Graphiti’s `Episode` node handles this elegantly.

---

## Minimal Working Set for the Experiment

1. Load three matters with versions v1–v4 into `Document`/`DocVersion`/`Clause` nodes.
2. For each Leah recommendation, create `AgentRecommendation` + optional `SuggestedEdit` + `Rationale` linked to the clause and review session.
3. When a user responds, log a `UserDecision` (and `Concession` if applicable) tied back to the recommendation.
4. Use the example queries to produce the KPIs:
   - Clause linkage: query 2
   - Recommendation adherence: queries 1 & 5
   - Handover reliability: query 4
   - Concession trail: query 3

This schema keeps the graph laser-focused on the negotiation storyline: what Leah suggested, what the user actually did, and how the contract evolved as a result.
