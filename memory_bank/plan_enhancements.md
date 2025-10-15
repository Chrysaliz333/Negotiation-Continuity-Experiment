# Plan Enhancements - Creative Session

**Created**: 2025-10-15
**Mode**: CREATIVE
**Session**: Plan Enhancement Based on Plain-English Goals

---

## User's Core Goals (Plain English)

1. **Shared Memory**: Team never loses track of past clause decisions, concessions, recommendations
2. **Quick Answers**: "What did we agree to last round?" / "Has this concession been granted?"
3. **Prove It Works**: Measure linking, handovers, concessions, override suppression

---

## Recommended Enhancements

### #1: Natural Language Query Interface ⭐ HIGH VALUE
**Add**: Day 4 (4-5 hours)

**Why**: Current plan has only Cypher queries. User wants "quick answers" in natural language.

**Approach**: Hybrid template library (10-15 common questions) with LLM fallback option

**Impact**: Enables actual demo of "What did we agree to?" use case

---

### #2: Proactive Suppression + Logging 🔥 CRITICAL
**Add**: Day 2 (2 hours)

**Why**: Current plan has suppression logic but no measurement/transparency

**Approach**: Transparent suppression with explanation ("Previously addressed by [User] on [date]")

**Impact**: Can measure suppression latency and rate (KPI requirements)

---

### #3: Handover Snapshot Pre-Packaging ⭐ HIGH VALUE
**Add**: Day 3 (3 hours)

**Why**: "Team collaboration" needs more than just queries - needs packaging

**Approach**: Round-based snapshot with JSON/Markdown/PDF export

**Impact**: Complete handover workflow, not just data retrieval

---

### #4: Synthetic Data Generator 🔥 CRITICAL - UNBLOCKS ALL
**Add**: Day 1 (4-6 hours)

**Why**: Current plan blocked by "ground truth data not ready"

**Approach**: Template-based generator with realistic variations

**Impact**: Unblocks Day 2-7, no waiting for manual data creation

---

### #5: Visual Timeline View 💎 NICE-TO-HAVE
**Add**: Day 5 (2 hours)

**Why**: Negotiations are temporal - timeline is more intuitive than tables

**Approach**: Simple matplotlib timeline with event types

**Impact**: Impressive demo visual, easier to understand history

---

## Updated Timeline

| Day | Original | Enhancements | Total Time |
|-----|----------|--------------|------------|
| 1 | Foundation (6h) | + Synthetic Data Generator (6h) | 12h |
| 2 | Graphiti Integration (8h) | + Suppression Logging (2h) | 10h |
| 3 | Ingestion + Queries (8h) | + Handover Packaging (3h) | 11h |
| 4 | Experiments (7h) | + NL Query Interface (3h) | 10h |
| 5 | Advanced Features (6h) | + Timeline Viz (2h) | 8h |
| 6-7 | Production Readiness | No changes | Original |

**Net Addition**: ~16 hours spread across 5 days (~3 hours per day)
**Feasibility**: Achievable with focused work sessions

---

## Priority Matrix

| Enhancement | User Value | Technical Complexity | ROI | Priority |
|-------------|------------|---------------------|-----|----------|
| #4: Synthetic Data | CRITICAL (unblocks) | Medium | HIGHEST | 1 |
| #2: Suppression Logging | HIGH (measurement) | Low | HIGH | 2 |
| #3: Handover Packaging | HIGH (workflow) | Medium | HIGH | 3 |
| #1: NL Query Interface | HIGH (demo) | Medium | HIGH | 4 |
| #5: Timeline Viz | MEDIUM (polish) | Low | MEDIUM | 5 |

---

## Implementation Guidelines

### Enhancement #4: Synthetic Data Generator (PRIORITY 1)

**File**: `scripts/generate/synthetic_data.py`

**Core Function**:
```python
def generate_matter(matter_id: str, num_versions: int = 4) -> Iterator[dict]:
    """Generate synthetic contract matter with realistic progression."""
    clauses = generate_base_clauses(count=20)  # Standard contract clauses

    for version in range(1, num_versions + 1):
        # Mutate 20-30% of clauses per version
        clauses = mutate_clauses(clauses, rate=0.25)

        # Generate 3-5 recommendations per version
        recommendations = generate_recommendations(clauses, count=random.randint(3, 5))

        # Generate decisions (70% apply, 20% override, 10% defer)
        decisions = generate_decisions(recommendations, distribution=[0.7, 0.2, 0.1])

        # 10% of decisions trigger concessions
        concessions = generate_concessions(decisions, rate=0.1)

        yield {
            "version": version,
            "clauses": clauses,
            "recommendations": recommendations,
            "decisions": decisions,
            "concessions": concessions,
        }
```

**Variation Strategies**:
- Clause templates: Liability, Indemnification, Termination, Warranty, IP, Confidentiality
- Text mutations: Paraphrasing, add/remove qualifiers, change numbers
- Issue types: Risk, Consent, One-sided, Missing protection, Ambiguity
- Decision rationales: Template-based realistic reasons

**Output**: 3 matters × 4 versions = 12 JSON files in `data/ground_truth/synthetic_*/*.json`

---

### Enhancement #2: Suppression Logging (PRIORITY 2)

**File**: `scripts/ingest/suppression_logger.py`

**Core Function**:
```python
def check_and_log_suppression(
    clause_id: str,
    issue_type: str
) -> Optional[SuppressionEvent]:
    """Check for existing override and log suppression if found."""

    override = query_existing_override(clause_id, issue_type)

    if override:
        event = SuppressionEvent(
            clause_id=clause_id,
            issue_type=issue_type,
            suppressed_at=datetime.now(),
            original_override_id=override.decision_id,
            original_override_by=override.actor,
            original_override_date=override.ts,
            original_override_reason=override.notes,
        )

        log_to_metrics(event)  # For KPI measurement

        return event

    return None
```

**Integration Point**: Call before recommendation generation in ingestion pipeline

**Metrics Tracked**:
- Suppression latency (time from override to first suppression check)
- Suppression rate (% of potential re-recommendations suppressed)
- False negatives (cases where suppression should have happened but didn't)

---

### Enhancement #3: Handover Packaging (PRIORITY 3)

**File**: `analytics/handover.py`

**Core Function**:
```python
def generate_handover_package(
    from_version: str,
    to_version: str,
    format: str = "markdown"
) -> Union[str, dict]:
    """Generate complete handover package for version transition."""

    package = {
        "summary": {
            "from_version": from_version,
            "to_version": to_version,
            "transition_date": get_version_date(to_version),
            "clauses_changed": count_changed_clauses(from_version, to_version),
            "recommendations_count": count_recommendations(to_version),
            "decisions_made": count_decisions(to_version),
            "concessions_granted": count_concessions(to_version),
            "open_items": count_pending_recommendations(to_version),
        },
        "changes": list_clause_changes(from_version, to_version),
        "recommendations": list_recommendations_with_status(to_version),
        "decisions": list_decisions_with_rationale(to_version),
        "concessions": list_concessions_with_impact(to_version),
        "action_items": list_pending_items(to_version),
    }

    if format == "markdown":
        return render_markdown(package)
    elif format == "json":
        return package
    elif format == "pdf":
        return render_pdf(package)
```

**Export Formats**:
- JSON: Programmatic access, API integration
- Markdown: Human-readable, email-friendly
- PDF: Printable, shareable with external parties

**Integration Point**: Add CLI command `python -m scripts.analytics.run_kpis handover --from v2 --to v3`

---

### Enhancement #1: NL Query Interface (PRIORITY 4)

**File**: `analytics/question_templates.py`

**Template Definition**:
```python
QUESTION_TEMPLATES = [
    {
        "name": "what_happened_in_round",
        "patterns": [
            r"what (happened|changed) (in|during) (round|version) (?P<round>\d+)",
            r"show (me )?changes (in|from) v(?P<round>\d+)",
        ],
        "cypher_template": """
            MATCH (v:DocVersion {version_no: $round})<-[:BELONGS_TO]-(c:Clause)
            OPTIONAL MATCH (c)-[:HAS_AGENT_RECOMMENDATION]->(rec)
            OPTIONAL MATCH (rec)<-[:APPLIES_TO]-(dec:UserDecision)
            RETURN c, rec, dec
        """,
        "result_formatter": format_version_changes,
    },
    {
        "name": "show_concessions",
        "patterns": [
            r"(show|list|what are) (the )?concessions?",
            r"what did (we|they) give up",
        ],
        "cypher_template": """
            MATCH (cons:Concession)-[:AFFECTS_CLAUSE]->(c:Clause)
            RETURN cons, c
            ORDER BY cons.ts DESC
        """,
        "result_formatter": format_concessions,
    },
    # ... 8-10 more common questions
]
```

**Query Translator**:
```python
class QueryTranslator:
    def __init__(self, templates: List[dict]):
        self.templates = templates

    def translate(self, question: str) -> Query:
        for template in self.templates:
            for pattern in template["patterns"]:
                if match := re.match(pattern, question, re.IGNORECASE):
                    params = match.groupdict()
                    return Query(
                        cypher=template["cypher_template"],
                        params=params,
                        formatter=template["result_formatter"],
                    )

        raise QueryNotRecognizedError(f"Cannot answer: {question}")
```

**Integration Point**: Add to `scripts/analytics/run_kpis.py ask "What concessions were granted?"`

---

### Enhancement #5: Timeline Visualization (PRIORITY 5)

**File**: `scripts/visualize/timeline.py`

**Core Function**:
```python
def generate_timeline(matter_id: str, output_path: str):
    """Generate visual timeline of negotiation history."""

    events = fetch_all_events(matter_id)  # Sorted by timestamp

    fig, ax = plt.subplots(figsize=(20, 8))

    event_types = {
        "version": {"y": 0, "marker": "o", "color": "#3498db", "label": "Version Upload"},
        "recommendation": {"y": 1, "marker": "^", "color": "#f39c12", "label": "Recommendation"},
        "apply": {"y": 2, "marker": "s", "color": "#2ecc71", "label": "Decision: Apply"},
        "override": {"y": 2, "marker": "X", "color": "#e74c3c", "label": "Decision: Override"},
        "concession": {"y": 3, "marker": "D", "color": "#e67e22", "label": "Concession"},
    }

    for event in events:
        style = event_types[event.type]
        ax.scatter(event.timestamp, style["y"],
                   marker=style["marker"],
                   color=style["color"],
                   s=100)
        ax.annotate(event.summary,
                    (event.timestamp, style["y"]),
                    fontsize=8, rotation=45)

    ax.set_yticks([0, 1, 2, 3])
    ax.set_yticklabels(["Versions", "Recommendations", "Decisions", "Concessions"])
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_path)
```

**Integration Point**: Add to experiment deliverables, one timeline per matter

---

## Updated Success Criteria

**Original Criteria** (from implementation_plan.md) remain unchanged, plus:

### New User Experience Criteria
- [ ] Natural language query interface answers ≥5 common question patterns
- [ ] Suppression events logged with full context (actor, date, reason)
- [ ] Handover packages generate in <5 seconds
- [ ] Timeline visualization renders complete negotiation history

### New Data Criteria
- [ ] Synthetic data generator creates 3 realistic matters
- [ ] Generated data passes all Pydantic validation
- [ ] Synthetic data exhibits realistic negotiation patterns (clause changes, decision distribution)

### New Measurement Criteria
- [ ] Suppression latency measured and < 200ms
- [ ] Suppression rate ≥ 95% (correctly suppresses 19 out of 20 repeat issues)
- [ ] Query answer accuracy ≥ 80% (NL questions correctly translated to Cypher)
- [ ] Handover package completeness = 100% (all version data captured)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Synthetic data not realistic enough | MEDIUM - Might not catch edge cases | Validate with 1-2 real matters before final experiment |
| NL query templates don't cover user questions | LOW - Can still use Cypher directly | Collect real question examples and iterate templates |
| Enhanced timeline adds scope creep | LOW - Optional feature | Deprioritize if running behind schedule |
| Suppression logging adds latency | LOW - Should be <10ms overhead | Profile and optimize if needed |

---

## Next Steps

1. **Approve enhancements** (or request modifications)
2. **Update `memory_bank/implementation_plan.md`** with enhanced timeline
3. **Update `memory_bank/tasks.md`** with new task items
4. **Begin Day 1 with synthetic data generator** (CRITICAL PATH)

---

**Status**: ✅ Creative phase complete, awaiting approval
**Recommended Next Mode**: IMPLEMENT (Day 1 with enhanced plan)
