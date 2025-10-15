from datetime import datetime, timezone

import pytest

from models import (
    AgentRecommendation,
    Clause,
    DocVersion,
    UserDecision,
    canonical_clause_id,
    canonical_decision_id,
    canonical_doc_id,
    canonical_recommendation_id,
    canonical_version_id,
)


def test_doc_version_source_constraint():
    dv = DocVersion(
        version_id="vid",
        doc_id="doc",
        version_no=1,
        source="agent",
        ts=datetime.now(timezone.utc),
    )
    assert dv.source == "agent"

    with pytest.raises(ValueError):
        DocVersion(
            version_id="bad",
            doc_id="doc",
            version_no=1,
            source="invalid",  # type: ignore[arg-type]
            ts=datetime.now(timezone.utc),
        )


def test_recommendation_trims_language():
    rec = AgentRecommendation(
        rec_id="rec",
        clause_id="clause",
        issue_type="consent",
        severity="high",
        suggested_action="EDIT",
        suggested_language="  replace text  ",
        ts=datetime.now(timezone.utc),
    )
    assert rec.suggested_language == "replace text"


def test_user_decision_trims_notes():
    decision = UserDecision(
        decision_id="dec",
        rec_id="rec",
        clause_id="clause",
        decision_type="OVERRIDE",
        actor="Attorney",
        ts=datetime.now(timezone.utc),
        notes="  handled offline  ",
    )
    assert decision.notes == "handled offline"


def test_canonical_doc_id_normalizes_title():
    doc_id_a = canonical_doc_id("matter-1", "Master Services Agreement")
    doc_id_b = canonical_doc_id("matter-1", "  master   services agreement ")
    assert doc_id_a == doc_id_b


def test_canonical_version_id_changes_with_inputs():
    ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
    version_id = canonical_version_id("doc", "msa_v1.docx", "user", ts)
    variant = canonical_version_id("doc", "msa_v1.docx", "user", ts)
    assert version_id == variant

    changed = canonical_version_id("doc", "msa_v2.docx", "user", ts)
    assert changed != version_id


def test_canonical_clause_and_recommendation_and_decision():
    clause = Clause(
        clause_id="clause-1",
        canonical_clause_id="canon-1",
        version_id="ver-1",
        section_path="1.2",
        text="Sample text",
    )
    clause_id = canonical_clause_id(
        clause.version_id,
        clause.section_path,
        clause.start_char,
        clause.end_char,
        clause.text_hash,
    )
    rec_id = canonical_recommendation_id(clause.clause_id, "Risk", datetime(2024, 1, 1, tzinfo=timezone.utc))
    decision_id = canonical_decision_id(rec_id, "Attorney", datetime(2024, 1, 1, tzinfo=timezone.utc))

    assert clause_id
    assert rec_id
    assert decision_id
    assert len(rec_id) == len(decision_id)
    assert clause.tags == []
    assert clause.playbook_flags == {}
