from __future__ import annotations

from datetime import datetime, timezone

from ai_research_os.contracts.base import DecisionCard, FeatureSnapshot, Hypothesis, RiskAssessment


class ProposalWorkflow:
    """最小 proposal workflow 骨架。

    真正实现时应依次接入：
    - feature generation
    - research hypothesis
    - risk review
    - committee merge
    - decision card delivery
    """

    def build_decision_card(
        self,
        *,
        snapshot: FeatureSnapshot,
        hypothesis: Hypothesis,
        risk: RiskAssessment,
    ) -> DecisionCard:
        action = "avoid" if risk.veto else "watch"
        return DecisionCard(
            proposal_id=hypothesis.proposal_id,
            trace_id=hypothesis.trace_id,
            agent_name="committee_agent",
            prompt_version=hypothesis.prompt_version,
            model_name=hypothesis.model_name,
            decision_card_id=f"dc_{snapshot.snapshot_id}",
            title=f"{snapshot.entity_ref} proposal",
            entity_refs=[snapshot.entity_ref],
            action=action,
            summary=hypothesis.thesis,
            why_now="Feature snapshot and hypothesis are aligned.",
            top_evidence=[f"{key}={value}" for key, value in list(snapshot.features.items())[:3]],
            key_risks=risk.reasons,
            trigger_conditions=[],
            invalidation_conditions=[],
            confidence=hypothesis.confidence,
            uncertainty_notes=[],
        )

    def next_tracking_horizons(self) -> list[tuple[str, datetime]]:
        now = datetime.now(timezone.utc)
        return [
            ("T+1", now),
            ("T+3", now),
            ("T+7", now),
            ("T+14", now),
        ]
