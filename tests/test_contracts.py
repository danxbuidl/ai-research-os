from datetime import datetime, timezone

from ai_research_os.contracts.base import DecisionCard, EvolutionProposal, Observation


def test_observation_contract() -> None:
    obs = Observation(
        proposal_id="prop_1",
        trace_id="trace_1",
        observation_id="obs_1",
        source_type="rss",
        event_time=datetime.now(timezone.utc),
        ingested_at=datetime.now(timezone.utc),
        content_type="news",
        payload={"title": "hello"},
    )
    assert obs.source_type == "rss"


def test_decision_card_contract() -> None:
    card = DecisionCard(
        proposal_id="prop_1",
        trace_id="trace_1",
        decision_card_id="dc_1",
        title="BTC watch",
        entity_refs=["BTC"],
        action="watch",
        summary="summary",
        why_now="why now",
    )
    assert card.action == "watch"


def test_evolution_proposal_contract() -> None:
    evo = EvolutionProposal(
        proposal_id="prop_1",
        trace_id="trace_1",
        evolution_proposal_id="evo_1",
        proposal_type="weights",
        scope="skill9",
        challenger_name="skill9_v2",
        hypothesis="new derivatives weights improve precision",
        change_summary="Increase derivatives weight by 0.1",
        created_at=datetime.now(timezone.utc),
    )
    assert evo.status == "candidate"
