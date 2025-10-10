# Negotiation Continuity Experiment — Agent Playbook

## Mission
Stand up and evaluate a knowledge-graph-driven continuity layer for contract negotiations focused exclusively on a Graphiti + FalkorDB stack (with optional Amazon Neptune path). Measure continuity KPIs: clause linkage, decision consistency, handover reliability, contradiction detection, and policy drift coverage.

## High-Level Workflow
1. **Dataset Preparation**
   - Collect 3–5 matters with versions v1–v4.
   - Produce ground-truth annotations per version (`data/ground_truth/`): clause decisions, rationales, tags.
   - Ensure deterministic identifiers (`doc_id`, `version_id`, `clause_id`).

2. **Graphiti + Falkor Prototype**
   - Launch FalkorDB (Docker) and install `graphiti-core[falkordb]`.
   - Define Pydantic entities that map Agreement/Clause/Decision/Rationale into Graphiti episodes.
   - Build an ingestion adapter that streams contract versions + decision logs with temporal metadata.
   - Implement a retrieval gateway (Graphiti hybrid search) that returns latest clause state, lineage, related policies, rationale.

3. **Continuity Experiment Runs**
   - Architecture under test:
     - Agent + Graphiti (Falkor backend) with optional Neptune evaluation.
   - For each scenario (negotiation loop, lawyer handover, policy drift, cross-matter):
     - Run standardized tasks.
     - Log metrics: continuity linking, decision consistency, handover reliability, contradiction rate, drift alerts, latency.

4. **Production Readiness Tasks**
   - Evaluate Falkor Cloud provisioning scripts.
   - Trial Graphiti with `graphiti-core[neptune]` against Amazon Neptune/Neptune Analytics.
   - Summarize trade-offs for Neo4j vs Falkor vs Neptune (performance, ops, licensing).

## Key Artifacts
- `docs/TODO.md` — master checklist.
- `docs/kg_schema_mve.md` — updated KG schema (entities, edges, keys, example queries).
- `data/ground_truth/` — annotated versions (JSON schema enforced via merge script).
- `scripts/ground_truth/merge_annotations.py` — merges reviewer spreadsheets into canonical JSON.
- `scripts/replay/harness.py` — pauses/resumes agent workflows to measure resilience.
- Experiment notebooks/dashboard — compare KPIs across architectures A/B/C.

## Environment Setup
1. **Python**: 3.10+ (recommend `uv` or `python -m venv .venv` + `source .venv/bin/activate`).
2. **Core deps** (draft):
   ```bash
   pip install -r requirements.txt              # base tools
   pip install "graphiti-core[falkordb]"       # Graphiti + Falkor support
   pip install "graphiti-core[neptune]"        # (optional) Neptune testing
   pip install pandas pydantic rich typer       # helpers for scripts
   ```
3. **Services**:
   - FalkorDB via Docker: `docker run -p 6379:6379 -p 3000:3000 falkordb/falkordb:latest`
   - Neo4j (existing baseline) if needed for comparison.
   - Optional Neptune sandbox (AWS credentials required).

4. **Environment variables** (`.env` template):
   ```env
   OPENAI_API_KEY=...
   FALKORDB_HOST=localhost
   FALKORDB_PORT=6379
   GRAPHITI_TELEMETRY_ENABLED=false
   SEMAPHORE_LIMIT=10
   # Optional
   NEPTUNE_ENDPOINT=...
   AOSS_HOST=...
   ```

## Execution Notes for Agents
- **Extraction**: Reuse existing extractor outputs; ensure `contract_id` stability.
- **Validation**: Run the ground-truth merge validator before ingestion.
- **Logging**: Persist experiment metrics to `data/metrics/*.jsonl` for comparison.
- **Telemetry**: Disable Graphiti telemetry unless approved (`GRAPHITI_TELEMETRY_ENABLED=false`).
- **Credentials**: Never commit `.env` or secrets.
- **Ops hygiene**: Document Docker commands, port usage, and cleanup steps in `docs/ENVIRONMENT.md`.

## Deliverables
- Falkor-backed Graphiti prototype with ingestion + retrieval adapters.
- Experiment results (tables/plots) demonstrating KPI performance of the Graphiti stack across all scenarios.
- Integration guide for production (Falkor vs Neptune) with ops considerations.
- Recommendations memo summarizing continuity improvements and next steps.

Stay disciplined: commit frequently, keep README/quickstart docs aligned, and update the TODO checklist as tasks complete.
