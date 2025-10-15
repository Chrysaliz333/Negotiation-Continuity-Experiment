# Implementation Plan - Level 3 Comprehensive

**Created**: 2025-10-15
**Mode**: PLAN
**Complexity**: Level 3 (Moderately Complex)
**Project**: Negotiation Continuity Experiment

---

## Plan Overview

This plan details the implementation strategy for building a knowledge-graph continuity layer for contract negotiations using Graphiti + FalkorDB. The project is scoped for 7-day completion with clear phase dependencies and success criteria.

### Current State Assessment

**✅ Already Complete:**
- Pydantic entity models (`models/entities.py`) - 9 core entities defined
- Canonical ID generation (`models/ids.py`) - Deterministic hash functions
- Basic ingestion CLI scaffold (`scripts/ingest/load_graphiti.py`)
- Query templates (`analytics/kpi_queries.py`) - 4 KPI query templates
- Unit tests (`tests/test_models.py`) - Model validation tests
- Requirements defined (`requirements.txt`)

**⚠️ Notable Gaps:**
- No ground truth data yet in `data/ground_truth/`
- Graphiti integration layer not implemented (Episode creation, graph writes)
- FalkorDB environment not verified
- Query execution engine not implemented
- Experiment harness not built
- No visualization or metrics tracking

---

## Requirements Analysis

### Functional Requirements

1. **Data Ingestion**
   - Ingest contract documents with multiple versions (v1-v4)
   - Create Graphiti episodes for each ingestion event
   - Establish clause lineage across versions via `EVOLVES_TO` edges
   - Link recommendations to clauses with rationales
   - Record user decisions and concessions

2. **Query & Retrieval**
   - Clause linkage queries (precision/recall measurement)
   - Recommendation adherence tracking (apply vs override vs defer)
   - Handover snapshots (session context completeness)
   - Concession trail tracking
   - Override suppression lookups

3. **KPI Measurement**
   - Automated KPI calculation across experiment scenarios
   - Metrics logging to JSONL format
   - Comparison against baseline targets

4. **Production Readiness**
   - FalkorDB vs Neptune evaluation
   - Monitoring and health checks
   - Integration documentation

### Non-Functional Requirements

- **Performance**: <200ms p95 query latency, >10 matters/hour ingestion
- **Reliability**: Deterministic IDs, bi-temporal edges for audit trail
- **Scalability**: Support 3-5 matters initially, design for 10×
- **Maintainability**: Clear separation of concerns, comprehensive tests

---

## Components Affected

### 1. Data Models & Validation (`models/`)
**Status**: ✅ 80% Complete

**Existing**:
- `entities.py` - 9 Pydantic models (Document, DocVersion, Clause, AgentRecommendation, SuggestedEdit, Rationale, UserDecision, Concession, ReviewSession, Episode)
- `ids.py` - Canonical ID generation with SHA256 hashing
- `__init__.py` - Module exports

**Remaining Work**:
- Add `Party` entity model (referenced in schema but not implemented)
- Add helper methods for episode metadata generation
- Extend validation for bi-temporal field constraints
- Add JSON schema export for ground truth validation

### 2. Ingestion Pipeline (`scripts/ingest/`)
**Status**: 🟡 30% Complete

**Existing**:
- `load_graphiti.py` - CLI scaffold with validation and dry-run mode
- Configuration loading from `.env`
- JSON payload parsing and Pydantic validation

**Remaining Work** (🎨 **CREATIVE REQUIRED**):
- Graphiti client initialization and connection management
- Episode creation strategy for different event types
- Node upsert logic (documents, versions, clauses)
- Edge creation logic (BELONGS_TO, EVOLVES_TO, HAS_AGENT_RECOMMENDATION, etc.)
- Bi-temporal metadata management (t_valid, t_invalid, t_created, t_expired)
- Bulk ingestion with SEMAPHORE_LIMIT rate limiting
- Error handling and retry logic
- Progress tracking and logging

**Creative Design Decisions Needed**:
- Episode granularity (one per version vs one per clause change)
- Graph merge strategy (upsert vs replace)
- Temporal edge expiration logic
- Clause lineage detection algorithm

### 3. Query & Retrieval System (`analytics/`)
**Status**: 🟡 40% Complete

**Existing**:
- `kpi_queries.py` - 4 Cypher query templates (clause_lineage, outstanding_recommendations, handover_snapshot, concession_trail)
- Query parameterization framework

**Remaining Work**:
- Graphiti retrieval gateway initialization
- Query execution engine
- Result transformation and aggregation
- Precision/recall calculation for clause linkage
- Adherence percentage calculation for recommendations
- Context completeness scoring for handovers
- Concession visibility latency measurement

### 4. Analytics CLI (`scripts/analytics/`)
**Status**: ⚪ 0% Complete

**Needs Implementation**:
- `run_kpis.py` - CLI for executing KPI queries
- Connection to FalkorDB/Graphiti
- Parameter injection (session_id, canonical_clause_id, since date)
- Results formatting (tables, JSON, CSV)
- Metrics logging to `data/metrics/*.jsonl`
- Comparison against baseline targets

### 5. Ground Truth Data (`data/`)
**Status**: ⚪ 0% Complete (Data Dependency)

**Required**:
- `data/ground_truth/<matter_id>/*.json` - Annotated contract versions
- JSON schema enforcement
- `scripts/ground_truth/merge_annotations.py` - Spreadsheet merge script
- Smoke test dataset (1 matter, 4 versions)

### 6. Experiment Harness (`scripts/`)
**Status**: ⚪ 0% Complete

**Needs Implementation** (🎨 **CREATIVE REQUIRED**):
- `scripts/experiment/run_baseline.py` - Execute full experiment
- Scenario orchestration (negotiation loop, handover, concession tracking, cross-matter, override suppression)
- Metrics collection and aggregation
- Visualization generation (matplotlib/seaborn)
- `scripts/replay/harness.py` - Pause/resume workflow testing

**Creative Design Decisions Needed**:
- Experiment configuration format (YAML vs JSON)
- Scenario sequencing and isolation
- Metrics aggregation strategy
- Visualization layouts

### 7. Testing (`tests/`)
**Status**: 🟡 20% Complete

**Existing**:
- `test_models.py` - Model validation, ID generation tests

**Remaining Work**:
- `test_ingestion.py` - Ingestion pipeline integration tests
- `test_queries.py` - Query execution and results validation
- `test_kpis.py` - KPI calculation correctness
- Fixture generation for test data
- Integration tests with FalkorDB test instance

### 8. Documentation
**Status**: 🟡 60% Complete

**Existing**:
- README.md, AGENT.md, EXECUTIVE_SUMMARY.md, Memory Bank docs

**Remaining Work**:
- `ENVIRONMENT.md` - Docker setup, port usage, cleanup steps
- `INTEGRATION_GUIDE.md` - Production deployment instructions
- `RECOMMENDATIONS.md` - Findings and next steps
- Experiment report templates

---

## Architecture Considerations

### Temporal Model Strategy

**Bi-temporal Edge Pattern**:
- `t_created` / `t_expired` - System time (when we recorded the fact)
- `t_valid` / `t_invalid` - Real-world time (when the fact was true in negotiation)

**Implementation Approach**:
1. On clause version ingestion, create new `BELONGS_TO` edge with `t_valid = version.ts`
2. Expire previous version's edge with `t_invalid = current_version.ts`
3. For queries: "Show contract as of date X" - filter edges where X is between `t_valid` and `t_invalid`

### Episode Provenance Pattern

**Episode Types**:
- `negotiation_round` - New contract version uploaded
- `agent_suggestion` - Leah generates recommendations
- `user_edit` - User applies/overrides/defers decision
- `ingestion_event` - Batch data load

**Linkage Strategy**:
All entities created in a single transaction share the same `episode_id`. This enables:
- Full audit trail reconstruction
- Rollback capability
- Provenance queries ("What recommendations came from Episode X?")

### Override Suppression Logic

**Pattern**:
```python
# Before generating recommendation for clause C on issue I:
existing_override = query("""
    MATCH (c:Clause {canonical_clause_id: $canon_id})-[:HAS_AGENT_RECOMMENDATION]->(rec)
    WHERE rec.issue_type = $issue_type
    MATCH (rec)<-[:APPLIES_TO]-(decision {decision_type: 'OVERRIDE'})
    RETURN decision
    LIMIT 1
""")
if existing_override:
    suppress_recommendation()
```

### Cross-Matter Precedent Design (🎨 **CREATIVE REQUIRED**)

**Challenge**: Link similar clauses across different matters

**Design Options**:
1. **Semantic embedding similarity**: Use Graphiti's hybrid search to find clauses with similar embeddings
2. **Clause type + risk level matching**: Index by `clause_type` + `risk_level`
3. **Playbook tag intersection**: Match on `playbook_flags` overlap

**Needs Creative Exploration**: Trade-offs between precision, recall, and query performance

---

## Implementation Strategy

### Phase 1: Complete Core Infrastructure (Day 1)

**Parallel Work Streams**:

**Stream A: Data Foundation**
1. Implement `Party` entity model
2. Create JSON schema for ground truth validation
3. Build `merge_annotations.py` script stub
4. Set up `data/ground_truth/` directory structure with template

**Stream B: Environment Verification**
1. Start FalkorDB Docker container
2. Create Python virtual environment
3. Install dependencies from `requirements.txt`
4. Test FalkorDB connectivity
5. Validate `.env` configuration

**Stream C: Testing Infrastructure**
1. Create test fixtures for sample data
2. Set up pytest configuration
3. Add integration test markers
4. Create FalkorDB test database isolation

**Deliverables**:
- Virtual environment activated
- FalkorDB running on localhost:6379
- Test infrastructure ready
- Ground truth data template available

### Phase 2: Graphiti Integration Layer (Day 2) (🎨 **CREATIVE REQUIRED**)

**Critical Path**:
1. Design episode creation strategy (CREATIVE session recommended)
2. Implement Graphiti client wrapper
3. Build node upsert functions (Document, DocVersion, Clause)
4. Build edge creation functions (BELONGS_TO, HAS_VERSION, REVIEWED_IN)
5. Implement bi-temporal metadata handlers
6. Add logging and error handling

**Testing**:
- Unit tests for each upsert function
- Integration test: ingest 1 clause successfully
- Validate graph structure in FalkorDB browser (port 3000)

**Deliverables**:
- `graphiti_client.py` module with connection management
- `ingest_nodes.py` and `ingest_edges.py` with upsert logic
- Integration tests passing
- Documentation of design decisions

### Phase 3: Ingestion Pipeline Completion (Day 2-3)

**Build Order** (dependencies):
1. Implement recommendation ingestion (AgentRecommendation, SuggestedEdit, Rationale)
2. Implement decision ingestion (UserDecision, Concession)
3. Build clause lineage detection (EVOLVES_TO edge logic)
4. Add rate limiting with SEMAPHORE_LIMIT
5. Implement progress tracking

**Testing**:
- Smoke test: ingest 1 matter (4 versions) end-to-end
- Validate all entity types present in graph
- Validate edge relationships correct
- Check bi-temporal metadata populated

**Deliverables**:
- `load_graphiti.py` fully functional (dry_run=False works)
- Smoke test dataset ingested successfully
- Ingestion metrics logged (throughput, errors)

### Phase 4: Query Execution Engine (Day 3)

**Implementation**:
1. Create `graphiti_query_executor.py` module
2. Implement query execution with parameter injection
3. Add result transformation logic
4. Build KPI calculation functions:
   - Clause linkage: precision/recall from EVOLVES_TO graph
   - Recommendation adherence: count(applied) / count(total)
   - Handover completeness: % of clauses with full decision context
   - Concession visibility: latency to retrieve recent concessions

**Testing**:
- Test each query template against smoke test data
- Validate KPI calculations match hand-calculated values
- Performance test: query latency measurement

**Deliverables**:
- Query executor module complete
- KPI calculation functions tested
- Performance baseline established

### Phase 5: Analytics CLI & Metrics (Day 3-4)

**Implementation**:
1. Build `run_kpis.py` CLI with typer
2. Add query parameter configuration (CLI flags or config file)
3. Implement metrics logging to JSONL
4. Create result formatters (table, JSON, CSV)
5. Add comparison against baseline targets

**Testing**:
- End-to-end test: run all KPIs against smoke test data
- Validate metrics logged correctly
- Verify output formats

**Deliverables**:
- `run_kpis.py` fully functional
- Metrics logging working
- Sample KPI report generated

### Phase 6: Baseline Experiment (Day 4) (🎨 **CREATIVE REQUIRED**)

**Prerequisite**: 3-5 matters with ground truth data ready

**Implementation** (Creative design for orchestration):
1. Create experiment configuration format
2. Build `run_baseline.py` orchestrator
3. Implement scenario execution:
   - Negotiation loop continuity
   - Lawyer handover
   - Concession tracking
   - Cross-matter precedent (requires creative design)
   - Override suppression
4. Collect metrics per scenario
5. Generate aggregate results

**Testing**:
- Dry-run experiment with smoke test data
- Validate all scenarios execute
- Check metrics aggregation

**Deliverables**:
- Full experiment execution complete
- `data/metrics/graphiti_enhanced_baseline.jsonl` populated
- Baseline KPI measurements documented

### Phase 7: Visualization & Analysis (Day 4-5)

**Implementation**:
1. Create visualization scripts (matplotlib/seaborn)
2. Generate KPI comparison tables
3. Create charts:
   - Clause linkage precision/recall bar chart
   - Recommendation adherence pie chart
   - Handover completeness heatmap
   - Concession timeline
4. Document baseline performance

**Deliverables**:
- Visualizations generated
- Performance analysis document
- Optimization opportunities identified

### Phase 8: Advanced Features (Day 5-6)

**Override Suppression Enhancement**:
1. Implement suppression query in ingestion pipeline
2. Add warning when override detected
3. Test suppression logic

**Multi-Matter Precedent** (🎨 **CREATIVE REQUIRED**):
1. Design precedent matching algorithm (CREATIVE session)
2. Implement cross-matter queries
3. Test semantic similarity
4. Validate precedent retrieval accuracy

**Replay Harness**:
1. Build `scripts/replay/harness.py`
2. Implement pause/resume workflow simulation
3. Measure resilience metrics

**Deliverables**:
- Override suppression working
- Precedent search functional
- Replay harness tested

### Phase 9: Neptune Evaluation (Day 5 - Optional, Parallel)

**If AWS credentials available**:
1. Provision Neptune Analytics sandbox
2. Install `graphiti-core[neptune]`
3. Configure Neptune connection
4. Re-run baseline experiment with Neptune backend
5. Compare metrics:
   - Query latency
   - Ingestion throughput
   - Scalability (10× dataset if time permits)
   - Cost analysis

**Deliverables**:
- Neptune vs FalkorDB comparison table
- Trade-off analysis document

### Phase 10: Production Readiness (Day 6-7)

**Monitoring**:
1. Add Prometheus-compatible metrics exporters
2. Create health check endpoint
3. Add performance logging

**Documentation**:
1. Write `INTEGRATION_GUIDE.md` (production deployment)
2. Document FalkorDB vs Neptune decision framework
3. Create `ENVIRONMENT.md` (ops runbook)
4. Write `RECOMMENDATIONS.md` (findings and next steps)

**Validation**:
1. Run full KPI validation suite
2. Verify all success criteria met
3. Create reproducibility checklist
4. Final experiment report

**Deliverables**:
- Complete production documentation
- Recommendations memo
- All success criteria validated

---

## Detailed Steps

### Day 1: Foundation & Setup + 🔥 SYNTHETIC DATA GENERATOR (CRITICAL)

1. **Environment Setup** (1-2 hours)
   ```bash
   # Start FalkorDB
   docker run -p 6379:6379 -p 3000:3000 falkordb/falkordb:latest

   # Create venv
   python3 -m venv .venv
   source .venv/bin/activate

   # Install deps
   pip install -r requirements.txt

   # Configure .env
   cp .env.example .env
   # Fill in OPENAI_API_KEY, verify FALKORDB_HOST/PORT
   ```

2. **Add Party Entity** (30 min)
   - Add to `models/entities.py`
   - Update `models/__init__.py` exports
   - Add test to `tests/test_models.py`

3. **Ground Truth Infrastructure** (2-3 hours)
   - Create `data/ground_truth/` structure
   - Create JSON schema template
   - Build `scripts/ground_truth/merge_annotations.py` stub
   - Document expected data format

4. **Testing Infrastructure** (1-2 hours)
   - Create `tests/conftest.py` with fixtures
   - Add pytest configuration
   - Create test database isolation
   - Add integration test markers

5. **🔥 Synthetic Data Generator** (4-6 hours) **[ENHANCEMENT #4]**
   - Create `scripts/generate/synthetic_data.py`
   - Implement `generate_matter()` with realistic progression
   - Add clause templates (Liability, Indemnification, Termination, etc.)
   - Generate recommendations (3-5 per version)
   - Generate decisions (70% apply, 20% override, 10% defer)
   - Generate concessions (10% of decisions)
   - Generate 3 synthetic matters × 4 versions = 12 test files
   - **Output**: `data/ground_truth/synthetic_*/` directories
   - **IMPACT**: Unblocks Day 2-7 development immediately

### Day 2: Graphiti Integration (🎨 **CREATIVE SESSION**) + 🔥 SUPPRESSION LOGGING

**Morning: Creative Design Session (2-3 hours)**
- Episode granularity strategy
- Graph merge approach (upsert logic)
- Temporal edge management
- Error handling patterns

**Afternoon: Implementation (4-5 hours)**
1. Create `graphiti_client.py` wrapper
2. Implement node upsert functions
3. Implement edge creation functions
4. Add bi-temporal metadata
5. Write integration tests

**Late Afternoon: 🔥 Suppression Logging** (2 hours) **[ENHANCEMENT #2]**
6. Create `scripts/ingest/suppression_logger.py`
7. Implement `check_and_log_suppression()` function
8. Add suppression event logging to metrics
9. Integrate with recommendation generation pipeline
10. Add transparent suppression messages (show why recommendation was suppressed)
11. **Metrics tracked**: Suppression latency, suppression rate, false negatives
12. **IMPACT**: Can measure "stops nagging after override" KPI

### Day 3: Ingestion & Queries + ⭐ HANDOVER PACKAGING

**Morning: Complete Ingestion (3-4 hours)**
1. Recommendation ingestion
2. Decision ingestion
3. Clause lineage detection
4. Rate limiting
5. Smoke test ingestion

**Afternoon: Query Engine (3-4 hours)**
1. Query executor module
2. KPI calculation functions
3. Performance testing

**Late Afternoon: ⭐ Handover Packaging** (3 hours) **[ENHANCEMENT #3]**
4. Create `analytics/handover.py`
5. Implement `generate_handover_package()` function
6. Add round-based snapshot logic (from_version → to_version)
7. Build export formatters (JSON, Markdown, PDF)
8. Add CLI command: `run_kpis handover --from v2 --to v3`
9. Include: summary, changes, recommendations, decisions, concessions, action items
10. **IMPACT**: Complete team collaboration workflow ready

### Day 4: Experiments & Visualization + ⭐ NATURAL LANGUAGE QUERIES

**Morning: Experiment Design (2-3 hours)** (🎨 **CREATIVE SESSION**)
- Configuration format
- Scenario orchestration
- Metrics aggregation

**Mid-Day: ⭐ Natural Language Query Interface** (3 hours) **[ENHANCEMENT #1]**
1. Create `analytics/question_templates.py`
2. Define 10-15 common question templates with regex patterns
3. Implement `QueryTranslator` class
4. Add CLI command: `run_kpis ask "What concessions were granted?"`
5. Add to experiment: "Answer 5 natural language questions per matter"
6. **Examples**: "What happened in round 3?", "Show concessions", "What did we agree to?"
7. **IMPACT**: Can demo "quick answers" use case

**Afternoon: Execution & Analysis (4-5 hours)**
8. Run baseline experiment (including NL query scenario)
9. Generate visualizations
10. Document performance

### Day 5-6: Advanced Features + 💎 TIMELINE VIZ + Neptune

**Stream A: Advanced Features**
- Override suppression enhancement (already done Day 2)
- Multi-matter precedent (🎨 **CREATIVE SESSION** 2-3 hours)
- Replay harness implementation

**Stream A+: 💎 Timeline Visualization** (2 hours) **[ENHANCEMENT #5]**
- Create `scripts/visualize/timeline.py`
- Implement `generate_timeline()` function
- Plot event types: version uploads, recommendations, decisions, concessions
- Generate one timeline per matter
- **IMPACT**: Impressive visual demo for presentations

**Stream B: Neptune evaluation** (optional, parallel)
- Provision Neptune Analytics sandbox
- Re-run experiments
- Compare performance

### Day 7: Documentation & Validation

- Integration guide
- Recommendations memo
- Final validation
- Reproducibility checklist

---

## Dependencies

### Inter-Phase Dependencies

```
Phase 1 (Foundation)
  ↓
Phase 2 (Graphiti Integration) ← CREATIVE REQUIRED
  ↓
Phase 3 (Ingestion Pipeline)
  ↓
Phase 4 (Query Engine)
  ↓
Phase 5 (Analytics CLI)
  ↓
Phase 6 (Baseline Experiment) ← CREATIVE REQUIRED
  ↓
Phase 7 (Visualization)
  ↓
Phase 8 (Advanced Features) ← Multi-Matter CREATIVE REQUIRED
  ↓
Phase 10 (Production Readiness)

Phase 9 (Neptune) - Optional, parallel with Phase 5-8
```

### External Dependencies

- **Ground truth data**: Required by Day 3 for smoke test, Day 4 for full experiment
- **FalkorDB Docker**: Required by Day 1
- **OpenAI API key**: Required by Day 2 for embeddings (if using hybrid search)
- **AWS credentials**: Only for Phase 9 (Neptune evaluation)

### Component Dependencies

- Query execution depends on ingestion pipeline
- KPI calculation depends on query execution
- Experiment harness depends on both ingestion and KPI calculation
- Visualization depends on experiment results
- Documentation depends on all completed phases

---

## Challenges & Mitigations

| Challenge | Impact | Mitigation |
|-----------|--------|------------|
| Ground truth data not ready | HIGH - Blocks Day 3+ | Create synthetic data generator for testing; work with Liz to prepare real data by Day 3 |
| Episode granularity design complexity | MEDIUM - Affects graph size and query performance | Allocate 2-3 hours for CREATIVE design session Day 2; prototype both approaches |
| Clause lineage detection accuracy | MEDIUM - Core KPI measurement | Implement multiple matching strategies (text hash, position, semantic); compare precision/recall |
| Bi-temporal edge management complexity | MEDIUM - Schema correctness critical | Create dedicated test suite; validate against example scenarios from schema doc |
| Multi-matter precedent algorithm | HIGH - Requires creative design | Schedule CREATIVE session Day 5; explore hybrid semantic + structural matching |
| Neptune sandbox provisioning delay | LOW - Optional evaluation | Start provisioning Day 1; continue with FalkorDB if not ready by Day 5 |
| Query performance below targets | MEDIUM - KPI requirement | Add indexes on frequently queried fields; optimize Cypher queries; consider caching |
| Ingestion throughput below 10 matters/hour | LOW - Nice-to-have | Implement batch upserts; optimize SEMAPHORE_LIMIT; profile bottlenecks |

---

## Creative Phase Components

**🎨 Components Requiring CREATIVE Mode**:

1. **Graphiti Integration Strategy** (Day 2)
   - Episode granularity design
   - Graph merge approach
   - Temporal edge logic
   - **Recommendation**: CREATIVE session (2-3 hours)

2. **Experiment Orchestration** (Day 4)
   - Configuration format
   - Scenario sequencing
   - Metrics aggregation
   - **Recommendation**: CREATIVE session (1-2 hours)

3. **Multi-Matter Precedent Algorithm** (Day 5)
   - Matching strategy selection
   - Semantic vs structural trade-offs
   - Query optimization
   - **Recommendation**: CREATIVE session (2-3 hours)

**Total CREATIVE Time**: ~6-8 hours across 3 sessions

**Rationale**: These components involve significant design decisions with multiple viable approaches and performance trade-offs. Structured creative exploration will yield better outcomes than immediate implementation.

---

## Verification Checklist

### Plan Completeness

- [x] All requirements addressed
- [x] Components identified and scoped
- [x] Architecture considerations documented
- [x] Implementation steps defined
- [x] Dependencies mapped
- [x] Challenges identified with mitigations
- [x] Creative phases flagged
- [x] Testing strategy included
- [x] Timeline realistic (7 days)

### Technical Soundness

- [x] Pydantic models cover all schema entities
- [x] Canonical ID generation aligns with schema doc
- [x] Query templates match example queries
- [x] Bi-temporal pattern correctly understood
- [x] Episode provenance approach sound
- [x] KPI measurement methodology clear

### Resource Readiness

- [x] Python environment can be created
- [x] Dependencies installable
- [x] FalkorDB Docker available
- [ ] Ground truth data preparation plan (Liz)
- [ ] OpenAI API key available (Liz)
- [x] Optional Neptune credentials (not blocking)

---

## Success Criteria

### Technical Criteria

- [ ] All 9 entity types ingestible
- [ ] All 11 edge types created correctly
- [ ] Bi-temporal edges validated
- [ ] Episode provenance working
- [ ] 4 KPI queries execute successfully
- [ ] Query latency <200ms p95 (on smoke test data)
- [ ] Ingestion throughput measured
- [ ] Override suppression logic functional
- [ ] Tests passing (>80% coverage on core logic)

### Experiment Criteria

- [ ] Clause linkage: >90% precision, >85% recall
- [ ] Recommendation adherence: >75% resolved without repeats
- [ ] Handover reliability: >95% context completeness
- [ ] Concession visibility: <2 minutes to retrieve
- [ ] All 5 scenarios executed
- [ ] Metrics logged to JSONL
- [ ] Visualizations generated

### Deliverable Criteria

- [ ] Functional Graphiti + FalkorDB prototype
- [ ] Experiment results documented
- [ ] Integration guide complete
- [ ] Recommendations memo written
- [ ] Reproducible experiment setup
- [ ] Code committed to repository

### 🆕 Enhanced User Experience Criteria

- [ ] Natural language query interface answers ≥5 common question patterns
- [ ] Suppression events logged with full context (actor, date, reason)
- [ ] Handover packages generate in <5 seconds
- [ ] Timeline visualization renders complete negotiation history
- [ ] Can demo "What did we agree to?" and "Has this concession been granted?" queries

### 🆕 Enhanced Data Criteria

- [ ] Synthetic data generator creates 3 realistic matters
- [ ] Generated data passes all Pydantic validation
- [ ] Synthetic data exhibits realistic negotiation patterns (20-30% clause changes per version)
- [ ] Decision distribution matches realistic patterns (70% apply, 20% override, 10% defer)

### 🆕 Enhanced Measurement Criteria

- [ ] Suppression latency measured and < 200ms
- [ ] Suppression rate ≥ 95% (correctly suppresses 19 out of 20 repeat issues)
- [ ] Query answer accuracy ≥ 80% (NL questions correctly translated to Cypher)
- [ ] Handover package completeness = 100% (all version data captured)

---

## Next Steps After PLAN Mode

1. **If creative phases required** (YES - 3 components identified):
   - Transition to **CREATIVE mode** for Graphiti Integration Strategy (Day 2)
   - Return to IMPLEMENT mode after each creative session

2. **For straightforward components**:
   - Transition directly to **IMPLEMENT mode**
   - Follow phased approach (Day 1 → Day 7)

3. **Mode Progression**:
   ```
   PLAN (complete) → CREATIVE (enhancements approved) → IMPLEMENT (Day 1 with synthetic data) →
   CREATIVE (Graphiti Integration Day 2) → IMPLEMENT (Phase 2-3) →
   CREATIVE (Experiment Orchestration Day 4) → IMPLEMENT (Phase 4-7) →
   CREATIVE (Multi-Matter Precedent Day 5) → IMPLEMENT (Phase 8-10) →
   QA (Final validation)
   ```

---

## 🆕 Plan Enhancements Summary

**5 Enhancements Integrated** (See `memory_bank/plan_enhancements.md` for full details):

1. **🔥 Synthetic Data Generator** (Day 1, 4-6h) - CRITICAL - Unblocks all development
2. **🔥 Suppression Logging** (Day 2, 2h) - CRITICAL - Enables measurement KPIs
3. **⭐ Handover Packaging** (Day 3, 3h) - HIGH VALUE - Team collaboration ready
4. **⭐ NL Query Interface** (Day 4, 3h) - HIGH VALUE - "Quick answers" demo-able
5. **💎 Timeline Visualization** (Day 5, 2h) - NICE-TO-HAVE - Visual polish

**Total Added Time**: ~16 hours (~3h per day over 5 days)
**Net Impact**: Project goals fully aligned with plain-English requirements

---

**Plan Status**: ✅ Complete, verified, and enhanced
**Enhancements**: ✅ All 5 integrated into timeline
**Recommended Next Mode**: **IMPLEMENT** (Day 1 with synthetic data generator)
**Alternative**: Review `memory_bank/plan_enhancements.md` for detailed enhancement analysis
