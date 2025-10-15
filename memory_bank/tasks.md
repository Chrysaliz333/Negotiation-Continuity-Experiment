# Tasks - Single Source of Truth

**Last Updated**: 2025-10-15
**Current Phase**: Pre-Implementation (Transitioning to PLAN)
**Project**: Negotiation Continuity Experiment

---

## Phase 0: Foundation (COMPLETED)
- [x] Memory Bank initialization
- [x] Project documentation review
- [x] Technology stack confirmation

---

## Phase 1: Schema & Data Models + 🔥 SYNTHETIC DATA (PENDING)
### Core Models
- [ ] Add `Party` entity model (missing from current implementation)
- [ ] Add helper methods for episode metadata generation
- [ ] Extend validation for bi-temporal field constraints
- [ ] Add JSON schema export for ground truth validation

### Ground Truth Preparation
- [ ] Create `data/ground_truth/` structure
- [ ] Create JSON schema template
- [ ] Build `scripts/ground_truth/merge_annotations.py` stub
- [ ] Document expected data format

### 🔥 Synthetic Data Generator (ENHANCEMENT #4 - CRITICAL)
- [ ] Create `scripts/generate/synthetic_data.py`
- [ ] Implement `generate_matter()` function with realistic progression
- [ ] Add clause templates (Liability, Indemnification, Termination, Warranty, IP, Confidentiality)
- [ ] Implement recommendation generator (3-5 per version)
- [ ] Implement decision generator (70% apply, 20% override, 10% defer)
- [ ] Implement concession generator (10% of decisions)
- [ ] Generate 3 synthetic matters × 4 versions = 12 test files
- [ ] Validate generated data passes Pydantic validation
- [ ] Test synthetic data exhibits realistic patterns

**Dependencies**: None
**Owner**: Liz
**Estimated Duration**: Day 1 (10-12 hours with synthetic data)

---

## Phase 2: Graphiti + FalkorDB Integration + 🔥 SUPPRESSION (PENDING)
### Environment Setup
- [ ] Verify FalkorDB Docker container running
- [ ] Install `graphiti-core[falkordb]` dependencies
- [ ] Configure `.env` with FalkorDB connection details
- [ ] Test FalkorDB connectivity

### Ingestion Pipeline (CREATIVE SESSION REQUIRED)
- [ ] CREATIVE: Design episode creation strategy
- [ ] CREATIVE: Design graph merge approach
- [ ] CREATIVE: Design temporal edge management
- [ ] Implement Graphiti client wrapper (`graphiti_client.py`)
- [ ] Implement node upsert functions (Document, DocVersion, Clause)
- [ ] Implement edge creation functions (BELONGS_TO, HAS_VERSION, REVIEWED_IN, etc.)
- [ ] Build temporal metadata handlers (bi-temporal edges)
- [ ] Implement SEMAPHORE_LIMIT rate limiting
- [ ] Add logging and error handling

### 🔥 Suppression Logging (ENHANCEMENT #2 - CRITICAL)
- [ ] Create `scripts/ingest/suppression_logger.py`
- [ ] Implement `check_and_log_suppression()` function
- [ ] Add suppression event logging to metrics
- [ ] Integrate with recommendation generation pipeline
- [ ] Add transparent suppression messages (show context)
- [ ] Track suppression latency metric
- [ ] Track suppression rate metric
- [ ] Test suppression detection accuracy

### Smoke Test
- [ ] Ingest 1 synthetic matter (4 versions) into Graphiti
- [ ] Verify schema compliance in FalkorDB
- [ ] Query basic clause linkage
- [ ] Validate temporal edge creation
- [ ] Test suppression logic with override scenario

**Dependencies**: Phase 1 complete
**Estimated Duration**: Day 2 (10 hours with suppression)

---

## Phase 3: Retrieval & Query System + ⭐ HANDOVER (PENDING)
### Query Implementation
- [ ] Create `graphiti_query_executor.py` module
- [ ] Implement query execution with parameter injection
- [ ] Add result transformation logic
- [ ] Implement Cypher query for clause linkage (precision/recall)
- [ ] Implement query for recommendation adherence stats
- [ ] Implement query for handover context completeness
- [ ] Implement query for concession tracking and visibility
- [ ] Build KPI calculation functions (precision, recall, adherence %, etc.)

### Retrieval Gateway
- [ ] Build Graphiti hybrid search adapter
- [ ] Implement latest clause state queries
- [ ] Implement lineage traversal queries
- [ ] Add recommendation and rationale retrieval
- [ ] Implement point-in-time queries (bi-temporal)

### ⭐ Handover Packaging (ENHANCEMENT #3 - HIGH VALUE)
- [ ] Create `analytics/handover.py` module
- [ ] Implement `generate_handover_package()` function
- [ ] Add round-based snapshot logic (from_version → to_version)
- [ ] Build JSON export formatter
- [ ] Build Markdown export formatter
- [ ] Build PDF export formatter
- [ ] Add CLI command: `run_kpis handover --from v2 --to v3`
- [ ] Include summary, changes, recommendations, decisions, concessions, action items
- [ ] Test handover package generation speed (<5 seconds)
- [ ] Validate 100% context completeness

### Analytics CLI
- [ ] Build `run_kpis.py` CLI with typer
- [ ] Add query parameter configuration
- [ ] Implement metrics logging to JSONL
- [ ] Create result formatters (table, JSON, CSV)
- [ ] Add comparison against baseline targets

**Dependencies**: Phase 2 complete
**Estimated Duration**: Day 3 (11 hours with handover)

---

## Phase 4: Baseline Experiment + ⭐ NATURAL LANGUAGE QUERIES (PENDING)
### ⭐ Natural Language Query Interface (ENHANCEMENT #1 - HIGH VALUE)
- [ ] Create `analytics/question_templates.py` module
- [ ] Define 10-15 common question templates with regex patterns
- [ ] Implement `QueryTranslator` class
- [ ] Add CLI command: `run_kpis ask "What concessions were granted?"`
- [ ] Test question patterns: "What happened in round 3?", "Show concessions", etc.
- [ ] Add NL query scenario to experiment
- [ ] Measure query answer accuracy (target ≥80%)

### Experiment Design (CREATIVE SESSION REQUIRED)
- [ ] CREATIVE: Design experiment configuration format (YAML vs JSON)
- [ ] CREATIVE: Design scenario sequencing and isolation
- [ ] CREATIVE: Design metrics aggregation strategy
- [ ] Create `scripts/experiment/run_baseline.py` orchestrator

### Data Preparation
- [ ] Use 3 synthetic matters from Phase 1
- [ ] Validate all ground truth annotations
- [ ] Create experiment configuration file

### Experiment Execution
- [ ] Run ingestion for all matters
- [ ] Execute KPI queries across all scenarios:
  - [ ] Negotiation loop continuity
  - [ ] Lawyer handover
  - [ ] Concession tracking
  - [ ] Cross-matter precedent
  - [ ] Override suppression
  - [ ] Natural language query answering (NEW)
- [ ] Log metrics to `data/metrics/graphiti_enhanced_baseline.jsonl`

### Analysis
- [ ] Generate KPI comparison tables
- [ ] Create visualization plots
- [ ] Document baseline performance
- [ ] Identify optimization opportunities

**Dependencies**: Phase 3 complete
**Estimated Duration**: Day 4 (10 hours with NL queries)

---

## Phase 5: Advanced Features + 💎 TIMELINE VIZ (PENDING)
### Override Suppression Enhancement
- [ ] Already implemented in Phase 2 ✅
- [ ] Verify suppression logic working end-to-end
- [ ] Validate metrics collection

### Multi-Matter Precedent (CREATIVE SESSION REQUIRED)
- [ ] CREATIVE: Design precedent matching algorithm
- [ ] CREATIVE: Semantic vs structural trade-offs
- [ ] CREATIVE: Query optimization strategy
- [ ] Implement cross-matter relationship queries
- [ ] Add precedent search functionality
- [ ] Test semantic similarity across matters
- [ ] Validate precedent retrieval accuracy

### 💎 Timeline Visualization (ENHANCEMENT #5 - NICE-TO-HAVE)
- [ ] Create `scripts/visualize/timeline.py` module
- [ ] Implement `generate_timeline()` function
- [ ] Plot version uploads (blue circles)
- [ ] Plot recommendations (yellow triangles)
- [ ] Plot decisions (green squares = apply, red X = override)
- [ ] Plot concessions (orange diamonds)
- [ ] Generate one timeline per matter
- [ ] Test timeline rendering

### Replay Harness
- [ ] Update replay/guardrail harness (`scripts/replay/harness.py`)
- [ ] Add pause/resume functionality
- [ ] Implement resilience measurements
- [ ] Test workflow interruption scenarios

**Dependencies**: Phase 4 complete
**Estimated Duration**: Day 5-6 (8 hours with timeline)

---

## Phase 6: Neptune Evaluation (OPTIONAL - PENDING)
- [ ] Provision Neptune Analytics sandbox
- [ ] Install `graphiti-core[neptune]`
- [ ] Configure Neptune connection
- [ ] Re-run baseline experiment with Neptune backend
- [ ] Compare performance metrics:
  - [ ] Query latency
  - [ ] Ingestion throughput
  - [ ] Scalability (10× dataset)
  - [ ] Cost analysis
- [ ] Document FalkorDB vs Neptune trade-offs

**Dependencies**: Phase 4 complete
**Estimated Duration**: Day 5 (parallel with Phase 5)

---

## Phase 7: Production Readiness (PENDING)
### Monitoring
- [ ] Set up Prometheus-compatible metrics exporters
- [ ] Create Grafana dashboards (optional)
- [ ] Implement health check endpoints
- [ ] Add performance logging

### Documentation
- [ ] Write integration guide for production deployment
- [ ] Document FalkorDB vs Neptune decision framework
- [ ] Create operations runbook
- [ ] Write recommendations memo

### Validation
- [ ] Run full KPI validation suite
- [ ] Verify all success criteria met
- [ ] Create reproducibility checklist
- [ ] Final experiment report

**Dependencies**: Phase 5 (and optionally Phase 6) complete
**Estimated Duration**: Day 6-7

---

## Nice-to-Have (Post-Baseline)
- [ ] RDF/SHACL export adapter for external ontology view
- [ ] Advanced visualization dashboard
- [ ] Automated regression testing suite
- [ ] Performance optimization based on profiling
- [ ] Extended ground truth dataset (10+ matters)

---

## Blocked/Waiting
_Currently empty_

---

## Notes
- Project complexity: **Level 3** (moderately complex)
- Mode progression: VAN → PLAN → CREATIVE → IMPLEMENT → QA
- Source files: `TODO.md`, `AGENT.md`, `EXECUTIVE_SUMMARY.md`
- Reference schema: `kg_schema_graphiti_enhanced.md`
- Implementation guide: `graphiti-analysis-recommendations.md`
