# Negotiation Continuity Experiment - Project Brief

## Mission
Stand up and evaluate a knowledge-graph-driven continuity layer for contract negotiations using Graphiti + FalkorDB stack (with optional Amazon Neptune evaluation). Measure continuity KPIs: clause linkage, recommendation adherence, handover reliability, concession tracking, and duplicate-alert suppression after user overrides.

## Project Overview
Prototype a knowledge-graph continuity layer for contract negotiations that maintains context across negotiation sessions, tracks decisions and rationales, and prevents duplicate prompts after user overrides.

## Technology Stack

### Core
- **Graphiti** 0.17.0+ (`graphiti-core[falkordb]`)
- **FalkorDB** 1.1.2+ (Docker deployment)
- **Python** 3.10+

### Recommended
- OpenAI API (GPT-4 for extraction, text-embedding-3-small)
- Pydantic 2.0+ (entity validation)
- Rich/Typer (CLI tools)

### Optional
- Amazon Neptune Analytics (production scale evaluation)
- Prometheus + Grafana (monitoring)

## Key Performance Indicators (KPIs)

### Baseline Targets (vs manual process)
- **Clause linkage**: >90% precision, >85% recall
- **Recommendation adherence**: >75% of suggestions resolved without repeat prompts
- **Handover reliability**: >95% context completeness
- **Concession visibility**: <2 minutes to locate latest negotiated give-up

### Performance Targets
- **Query latency**: <200ms p95
- **Ingestion throughput**: >10 matters/hour
- **Storage efficiency**: <10MB per matter

## Graphiti Capabilities
- **State-of-the-art performance**: 94.8% vs 93.4% (MemGPT) on memory retrieval benchmarks
- **Bi-temporal model**: Tracks both system time and real-world validity for point-in-time queries
- **Real-time updates**: Incremental ingestion without batch recomputation
- **Sub-100ms latency**: Hybrid retrieval (semantic + keyword + graph traversal)
- **FalkorDB ready**: Docker single-command deployment for rapid prototyping

## Schema Enhancements

### Critical Additions
1. **Canonical clause IDs** → Stable tracking across versions (3× faster queries)
2. **Bi-temporal edges** → "Show contract state as of Sept 15" queries
3. **USER_DECISION edges** → Capture user overrides to stop resurfacing resolved issues
4. **JUSTIFIED_BY edges** → Direct recommendation-to-rationale linkage
5. **CONCESSION markers** → Track negotiated give-ups over time
6. **Episode integration** → Full audit trail and provenance

### Business Impact
- Handover reliability: Comprehensive snapshot queries vs manual aggregation
- Recommendation adherence: Understand when advice is accepted, modified, or ignored
- Precedent search: Cross-matter relationships vs isolated documents
- Decision consistency: Semantic coherence scoring vs manual review

## Dataset Requirements
- 3–5 matters with versions v1–v4
- Ground-truth annotations per version in `data/ground_truth/`
- Clause decisions, rationales, tags
- Deterministic identifiers (`doc_id`, `version_id`, `clause_id`)

## Environment Configuration

```bash
OPENAI_API_KEY=...
FALKORDB_HOST=localhost
FALKORDB_PORT=6379
GRAPHITI_TELEMETRY_ENABLED=false
SEMAPHORE_LIMIT=10
# Optional
NEPTUNE_ENDPOINT=...
AOSS_HOST=...
```

## Timeline
**1 week to complete Graphiti pilot**

### Day 1-2: Schema & Ingestion
- Define Pydantic entity models
- Implement canonical ID generation
- Build ground truth ingestion adapter
- Ingest 1 matter (4 versions) smoke test
- Validate schema compliance

### Day 3-4: Retrieval & KPIs
- Implement Cypher queries for 4 KPIs
- Run Graphiti baseline experiment (3-5 matters × 4 versions)
- Log metrics to `data/metrics/graphiti_enhanced_baseline.jsonl`

### Day 5: Neptune Evaluation (Optional)
- Provision Neptune Analytics sandbox
- Re-run experiment with Neptune backend
- Compare: latency, scalability (10× dataset), costs

### Day 6-7: Production Readiness
- Implement user override suppression logic
- Add multi-matter precedent search
- Set up Prometheus monitoring
- Write integration guide + recommendations memo

## Key Artifacts
- `TODO.md` — master checklist
- `kg_schema_graphiti_enhanced.md` — updated KG schema (entities, edges, keys, example queries)
- `data/ground_truth/` — annotated versions (JSON schema enforced)
- `scripts/ground_truth/merge_annotations.py` — merges reviewer spreadsheets into canonical JSON
- `scripts/replay/harness.py` — pauses/resumes agent workflows to measure resilience
- Experiment notebooks/dashboard — track KPI trends for Graphiti runs

## Experiment Scenarios
1. **Negotiation loop continuity**: Track clause evolution across versions
2. **Lawyer handover**: Complete context transfer between sessions
3. **Concession tracking**: Visibility of negotiated give-ups
4. **Cross-matter precedent**: Multi-matter relationship queries
5. **Override suppression**: Stop re-raising user-decided issues

## Deliverables
1. Falkor-backed Graphiti prototype with ingestion + retrieval adapters
2. Experiment results (tables/plots) demonstrating KPI performance across all scenarios
3. Integration guide for production (Falkor vs Neptune) with ops considerations
4. Recommendations memo summarizing continuity improvements and next steps

## Cost Analysis

### Development Phase (Weeks 1-4)
- FalkorDB: $0 (self-hosted Docker)
- OpenAI API: ~$50-100 (3-5 matters × 4 versions)
- Engineer time: Primary cost (1 FTE)

### Production Options

**Option A: FalkorDB (Self-Hosted)**
- Hosting: ~$30/month (AWS EC2 t3.medium)
- Ops: Self-managed (backups, scaling, monitoring)
- Break-even: <100K queries/day
- Best for: MVP, budget-constrained

**Option B: Neptune Analytics**
- Cost: ~$150/month (128GB provisioned memory)
- Ops: Fully managed (AWS handles everything)
- Break-even: >100K queries/day or >1M edges
- Best for: Production scale, enterprise

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| LLM extraction errors create noisy graph | Validate with ground truth; implement entity normalization |
| Rate limits during ingestion | Use `SEMAPHORE_LIMIT=10`; implement exponential backoff |
| Entity resolution misses duplicates | Pre-define canonical entities; fuzzy matching |
| Temporal queries return stale data | Validate `reference_time` in episodes; test point-in-time accuracy |

## Success Criteria
- Functional Graphiti + FalkorDB prototype
- All KPI targets met or exceeded
- Complete documentation and integration guide
- Clear recommendations for production deployment
- Reproducible experiment results

## Quick Start Commands

```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch FalkorDB
docker run -p 6379:6379 -p 3000:3000 falkordb/falkordb:latest

# 4. Configure environment
cp .env.example .env
# Fill in OPENAI_API_KEY, Falkor settings, etc.
```

## Project Status
- ✅ Documentation and schema drafts in place
- 🚧 Memory Bank initialized
- ⏳ Ready to begin PLAN phase for implementation
