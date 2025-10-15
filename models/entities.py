from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class Party(BaseModel):
    """Represents a party involved in the contract negotiation."""
    party_id: str
    name: str
    role: Literal["customer", "provider", "service_provider", "vendor", "client"]
    entity_type: Optional[Literal["individual", "company", "partnership", "government"]] = None
    jurisdiction: Optional[str] = None
    contact_info: Optional[str] = None


class Document(BaseModel):
    doc_id: str
    matter_id: str
    title: str
    counterparty: Optional[str] = None
    document_type: Optional[str] = None
    jurisdiction: Optional[str] = None
    created_at: Optional[datetime] = None


class DocVersion(BaseModel):
    version_id: str
    doc_id: str
    version_no: int
    source: Literal["customer", "counterparty", "agent"]
    ts: datetime
    hash: Optional[str] = None
    state: Optional[str] = None
    negotiation_round: Optional[int] = None


class Clause(BaseModel):
    clause_id: str
    canonical_clause_id: str
    version_id: str
    section_path: str
    clause_name: Optional[str] = None
    clause_type: Optional[str] = None
    text: str
    text_hash: Optional[str] = None
    start_char: Optional[int] = None
    end_char: Optional[int] = None
    page: Optional[int] = None
    word_count: Optional[int] = None
    risk_level: Optional[str] = None
    position_score: Optional[float] = None
    tags: List[str] = Field(default_factory=list)
    playbook_flags: Dict[str, Any] = Field(default_factory=dict)


class AgentRecommendation(BaseModel):
    rec_id: str
    clause_id: str
    issue_type: str
    severity: Literal["low", "medium", "high", "critical"]
    suggested_action: Literal["ACCEPT", "EDIT", "REMOVE"]
    suggested_language: Optional[str] = None
    status: Literal["pending", "applied", "overridden", "deferred"] = "pending"
    model_version: Optional[str] = None
    ts: datetime

    @field_validator("suggested_language")
    def strip_language(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return v.strip() or None


class SuggestedEdit(BaseModel):
    edit_id: str
    rec_id: str
    clause_id: str
    op: Literal["insert", "replace", "delete"]
    payload_json: dict
    proposed_by: str = Field(..., description="Actor identifier that proposed the edit")
    proposed_at: datetime


class Rationale(BaseModel):
    rationale_id: str
    rec_id: str
    rationale_text: str
    reasoning_type: Optional[Literal["risk_based", "precedent_based", "strategy"]] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    ts: datetime


class UserDecision(BaseModel):
    decision_id: str
    rec_id: str
    clause_id: str
    decision_type: Literal[
        "APPLY_RECOMMENDATION",
        "OVERRIDE",
        "DEFER",
        "CUSTOM_EDIT",
    ]
    status: Literal["logged", "implemented", "superseded"] = "logged"
    actor: str
    ts: datetime
    notes: Optional[str] = None

    @field_validator("notes")
    def strip_notes(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return v.strip() or None


class Concession(BaseModel):
    concession_id: str
    clause_id: str
    decision_id: str
    description: str
    trigger: Literal["user_initiated", "counterparty_pressure"]
    value_impact: Optional[str] = None
    ts: datetime


class ReviewSession(BaseModel):
    session_id: str
    actor: str
    ts_started: datetime
    ts_completed: Optional[datetime] = None
    summary: Optional[str] = None


class Episode(BaseModel):
    episode_id: str
    episode_type: Literal[
        "negotiation_round",
        "user_edit",
        "agent_suggestion",
        "ingestion_event",
    ]
    reference_time: datetime
    ingestion_time: datetime
    actor: Optional[str] = None
    tool_version: Optional[str] = None
    checksum: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
