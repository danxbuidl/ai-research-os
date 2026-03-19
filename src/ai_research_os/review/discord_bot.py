from __future__ import annotations

from typing import Iterable

from ai_research_os.contracts.base import DecisionCard


REJECT_REASON_TAGS: tuple[str, ...] = (
    "evidence_insufficient",
    "timing_wrong",
    "macro_conflict",
    "crowded_trade",
    "risk_not_covered",
    "wrong_mapping",
    "derivatives_overheated",
    "narrative_unconvincing",
    "poor_rr",
)


def render_decision_card_text(card: DecisionCard) -> str:
    evidence = "\n".join(f"- {item}" for item in card.top_evidence[:3]) or "- N/A"
    risks = "\n".join(f"- {item}" for item in card.key_risks[:2]) or "- N/A"
    triggers = "\n".join(f"- {item}" for item in card.trigger_conditions[:3]) or "- N/A"
    invalidations = "\n".join(f"- {item}" for item in card.invalidation_conditions[:3]) or "- N/A"

    return (
        f"**{card.title}**\n"
        f"Action: `{card.action}` | Confidence: `{card.confidence:.2f}`\n\n"
        f"Summary:\n{card.summary}\n\n"
        f"Why now:\n{card.why_now}\n\n"
        f"Top evidence:\n{evidence}\n\n"
        f"Key risks:\n{risks}\n\n"
        f"Triggers:\n{triggers}\n\n"
        f"Invalidations:\n{invalidations}\n\n"
        f"Audit:\n"
        f"- proposal_id: `{card.proposal_id}`\n"
        f"- trace_id: `{card.trace_id}`\n"
        f"- agent_name: `{card.agent_name}`\n"
        f"- prompt_version: `{card.prompt_version}`\n"
        f"- model_name: `{card.model_name}`"
    )


def default_review_actions() -> list[str]:
    return [
        "approve",
        "reject",
        "edit_and_approve",
        "hold",
        "need_more_evidence",
        "mark_lesson",
    ]


def normalize_reason_tags(tags: Iterable[str]) -> list[str]:
    allowed = set(REJECT_REASON_TAGS)
    return [tag for tag in tags if tag in allowed]
