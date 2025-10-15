# Negotiation Continuity Experiment

Knowledge-graph continuity layer for contract negotiations using Graphiti with FalkorDB backend (and optional Amazon Neptune evaluation). Tracks clause linkage, recommendation adherence, handover reliability, concession visibility, and suppresses repeat prompts after user overrides.

## Quick Start

1. **Create a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch FalkorDB for local testing**
   ```bash
   docker run -p 6379:6379 -p 3000:3000 falkordb/falkordb:latest
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Fill in OPENAI_API_KEY, FALKORDB_HOST, FALKORDB_PORT
   ```

5. **Review the implementation plan**
   - See `memory_bank/implementation_plan.md` for detailed 7-day plan
   - See `docs/planning/AGENT.md` for operational checklist

## Project Structure

```
negotiation-continuity/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment configuration template
│
├── memory_bank/                 # 🎯 CENTRAL SOURCE OF TRUTH
│   ├── projectbrief.md          # Project foundation and mission
│   ├── tasks.md                 # Task tracking (single source of truth)
│   ├── implementation_plan.md   # Detailed 10-phase implementation plan
│   ├── activeContext.md         # Current session focus
│   └── progress.md              # Implementation status dashboard
│
├── docs/                        # 📚 Documentation
│   ├── planning/
│   │   ├── EXECUTIVE_SUMMARY.md # Decision context and timeline
│   │   └── AGENT.md             # Operational checklist
│   ├── schema/
│   │   ├── kg_schema_graphiti_enhanced.md        # Canonical KG schema
│   │   └── graphiti-analysis-recommendations.md  # Implementation patterns
│   └── reference/
│       ├── clause_extraction_prompt.md           # Extraction guidelines
│       └── contract_negotiation_rules.md         # Business rules
│
├── models/                      # Pydantic entity models
│   ├── entities.py              # 9 core entities (Document, Clause, etc.)
│   ├── ids.py                   # Canonical ID generation
│   └── __init__.py
│
├── scripts/                     # CLI tools and automation
│   ├── ingest/
│   │   └── load_graphiti.py     # Ingestion pipeline (30% complete)
│   ├── analytics/
│   │   └── run_kpis.py          # KPI execution CLI (stub)
│   └── ground_truth/
│       └── merge_annotations.py # Spreadsheet merge (planned)
│
├── analytics/                   # Query modules
│   ├── kpi_queries.py           # 4 Cypher query templates
│   └── __init__.py
│
├── tests/                       # Test suite
│   └── test_models.py           # Model validation tests
│
├── data/                        # Data files
│   ├── ground_truth/            # Annotated contract versions (TBD)
│   ├── metrics/                 # Experiment results (generated)
│   └── raw/                     # Source data
│
└── custom_modes/                # Development mode instructions
    ├── van_instructions.md
    ├── plan_instructions.md
    ├── implement_instructions.md
    └── ...
```

## Key Documentation

### Start Here
- **`memory_bank/implementation_plan.md`** - Comprehensive 10-phase implementation plan (7 days)
- **`memory_bank/projectbrief.md`** - Mission, tech stack, KPIs, timeline
- **`memory_bank/tasks.md`** - Task breakdown by phase

### Planning & Strategy
- **`docs/planning/EXECUTIVE_SUMMARY.md`** - One-week delivery plan and decision context
- **`docs/planning/AGENT.md`** - Operational checklist for development

### Technical Schema
- **`docs/schema/kg_schema_graphiti_enhanced.md`** - Entity/relationship definitions, example queries
- **`docs/schema/graphiti-analysis-recommendations.md`** - Implementation patterns and code examples

### Reference
- **`docs/reference/clause_extraction_prompt.md`** - Clause extraction guidelines
- **`docs/reference/contract_negotiation_rules.md`** - Business rule definitions

## Current Status

**Phase**: Planning Complete (PLAN mode finished)
**Progress**: 20% implementation, 60% planning/design

### ✅ Completed
- Memory Bank infrastructure initialized
- Comprehensive 10-phase plan created
- Pydantic entity models (9/10 entities)
- Canonical ID generation
- Ingestion CLI scaffold
- Query templates (4 KPIs)
- Unit tests for models

### 🚧 In Progress
- Graphiti integration layer (requires CREATIVE session)
- Ground truth data preparation
- Query execution engine

### ⏳ Upcoming
- Environment setup (Day 1)
- Graphiti client implementation (Day 2)
- Full ingestion pipeline (Day 2-3)
- Baseline experiment (Day 4)
- Advanced features (Day 5-6)
- Production readiness (Day 6-7)

## Technology Stack

**Core:**
- Graphiti 0.17.0+ (`graphiti-core[falkordb]`)
- FalkorDB 1.1.2+ (Docker deployment)
- Python 3.10+

**Recommended:**
- OpenAI API (GPT-4 for extraction, text-embedding-3-small)
- Pydantic 2.0+ (entity validation)
- Rich/Typer (CLI tools)

**Optional:**
- Amazon Neptune Analytics (production scale evaluation)
- Prometheus + Grafana (monitoring)

## Key Performance Indicators

### Baseline Targets
- **Clause linkage**: >90% precision, >85% recall
- **Recommendation adherence**: >75% without repeat prompts
- **Handover reliability**: >95% context completeness
- **Concession visibility**: <2 minutes to locate

### Performance Targets
- **Query latency**: <200ms p95
- **Ingestion throughput**: >10 matters/hour
- **Storage efficiency**: <10MB per matter

## Development Workflow

The project uses a structured mode-based development approach:

1. **VAN Mode** (✅ Complete) - Initial assessment and Memory Bank setup
2. **PLAN Mode** (✅ Complete) - Comprehensive planning and architecture
3. **CREATIVE Mode** (Upcoming) - Design sessions for complex components:
   - Graphiti integration strategy (Day 2)
   - Experiment orchestration (Day 4)
   - Multi-matter precedent algorithm (Day 5)
4. **IMPLEMENT Mode** (Upcoming) - Systematic implementation by phase
5. **QA Mode** (Upcoming) - Final validation

See `custom_modes/` for detailed mode instructions.

## Next Steps

### Option A: Begin Implementation (Day 1 Foundation)
```bash
# Start FalkorDB
docker run -p 6379:6379 -p 3000:3000 falkordb/falkordb:latest

# Set up environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with OPENAI_API_KEY and connection details

# Run tests
pytest tests/
```

### Option B: Review Planning
- Read `memory_bank/implementation_plan.md` for detailed phase breakdown
- Review `docs/schema/kg_schema_graphiti_enhanced.md` for schema understanding
- Check `memory_bank/progress.md` for current status

## Contributors

Project managed via Memory Bank system with structured mode-based development.

## License

[Add license information]
