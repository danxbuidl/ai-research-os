from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ReleaseGateResult:
    allowed: bool
    reasons: list[str]


def replay_eval_available() -> bool:
    return True


def champion_challenger_available() -> bool:
    return True


def release_gate(*, golden_set_passed: bool, failure_set_passed: bool) -> ReleaseGateResult:
    reasons: list[str] = []
    if not golden_set_passed:
        reasons.append("golden_set_core failed")
    if not failure_set_passed:
        reasons.append("failure_set_recent failed")
    return ReleaseGateResult(allowed=not reasons, reasons=reasons)
