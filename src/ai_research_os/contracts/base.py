from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AuditFields(BaseModel):
    proposal_id: str
    trace_id: str
    agent_name: str = ""
    prompt_version: str = ""
    model_name: str = ""
    schema_version: str = "v1"


class Observation(AuditFields):
    observation_id: str
    source_type: str
    source_ref: str = ""
    asset_refs: list[str] = Field(default_factory=list)
    event_time: datetime
    ingested_at: datetime
    content_type: str
    payload: dict[str, Any] = Field(default_factory=dict)


class FeatureSnapshot(AuditFields):
    snapshot_id: str
    entity_type: str
    entity_ref: str
    as_of: datetime
    features: dict[str, Any] = Field(default_factory=dict)


class Hypothesis(AuditFields):
    hypothesis_id: str
    hypothesis_type: str
    entity_refs: list[str] = Field(default_factory=list)
    time_horizon: str
    thesis: str
    supporting_evidence: list[str] = Field(default_factory=list)
    key_risks: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    generated_at: datetime


class RiskAssessment(AuditFields):
    risk_assessment_id: str
    hypothesis_id: str
    risk_level: str
    can_proceed: bool = True
    veto: bool = False
    reasons: list[str] = Field(default_factory=list)
    position_limit_pct: float = 0.0


class DecisionCard(AuditFields):
    decision_card_id: str
    title: str
    entity_refs: list[str] = Field(default_factory=list)
    action: str
    summary: str
    why_now: str
    top_evidence: list[str] = Field(default_factory=list)
    key_risks: list[str] = Field(default_factory=list)
    trigger_conditions: list[str] = Field(default_factory=list)
    invalidation_conditions: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    uncertainty_notes: list[str] = Field(default_factory=list)
    review_actions: list[str] = Field(
        default_factory=lambda: [
            "approve",
            "reject",
            "edit_and_approve",
            "hold",
            "need_more_evidence",
            "mark_lesson",
        ]
    )


class HumanReview(AuditFields):
    review_id: str
    decision_card_id: str
    reviewer: str
    action: str
    reason_tags: list[str] = Field(default_factory=list)
    free_text: str = ""
    edited_fields: dict[str, Any] = Field(default_factory=dict)
    reviewed_at: datetime


class OutcomeRecord(AuditFields):
    outcome_id: str
    decision_card_id: str
    entity_ref: str
    horizon: str
    return_pct: float = 0.0
    max_drawdown_pct: float = 0.0
    hit_trigger: bool = False
    hit_invalidation: bool = False
    evaluated_at: datetime


class Lesson(AuditFields):
    lesson_id: str
    source_review_id: str
    lesson_type: str
    lesson_text: str
    scope: str
    status: str = "candidate"


class EvolutionProposal(AuditFields):
    evolution_proposal_id: str
    proposal_type: str
    scope: str
    challenger_name: str
    hypothesis: str
    change_summary: str
    expected_gain: str = ""
    risks: list[str] = Field(default_factory=list)
    validation_plan: list[str] = Field(default_factory=list)
    status: str = "candidate"
    created_at: datetime
