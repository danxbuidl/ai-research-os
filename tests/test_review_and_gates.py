from ai_research_os.contracts.base import DecisionCard
from ai_research_os.evaluation.gates import release_gate
from ai_research_os.review.discord_bot import normalize_reason_tags, render_decision_card_text


def test_render_decision_card_text_contains_audit_fields() -> None:
    card = DecisionCard(
        proposal_id="prop_1",
        trace_id="trace_1",
        agent_name="committee_agent",
        prompt_version="p1",
        model_name="deepseek/test",
        decision_card_id="dc_1",
        title="BTC watch",
        entity_refs=["BTC"],
        action="watch",
        summary="summary",
        why_now="why now",
        top_evidence=["ev1"],
        key_risks=["risk1"],
    )
    text = render_decision_card_text(card)
    assert "proposal_id" in text
    assert "committee_agent" in text


def test_normalize_reason_tags_filters_unknown_values() -> None:
    tags = normalize_reason_tags(["timing_wrong", "unknown", "poor_rr"])
    assert tags == ["timing_wrong", "poor_rr"]


def test_release_gate_blocks_when_any_eval_fails() -> None:
    result = release_gate(golden_set_passed=True, failure_set_passed=False)
    assert result.allowed is False
    assert result.reasons == ["failure_set_recent failed"]
