from __future__ import annotations

from datetime import UTC, datetime

from app.models.entities import Contract
from app.models.entities import Incidence


def compute_visit_score(contract: Contract | None, incidence: Incidence | None) -> float:
    sla_priority = contract.sla_priority if contract else 5
    sla_score = max(0.0, 100.0 - (sla_priority * 10.0))

    urgency_map = {
        "critical": 100.0,
        "high": 80.0,
        "medium": 55.0,
        "low": 25.0,
    }
    urgency_score = urgency_map.get((incidence.urgency_level if incidence else "medium").lower(), 55.0)
    impact_score = float(incidence.client_impact_score if incidence else 50)
    deadline_score = _deadline_score(incidence.due_at if incidence else None)

    return round(
        (sla_score * 0.40)
        + (urgency_score * 0.30)
        + (impact_score * 0.20)
        + (deadline_score * 0.10),
        2,
    )


def _deadline_score(due_at: datetime | None) -> float:
    if due_at is None:
        return 40.0

    now = datetime.now(UTC)
    due_aware = due_at if due_at.tzinfo else due_at.replace(tzinfo=UTC)
    hours_remaining = (due_aware - now).total_seconds() / 3600

    if hours_remaining <= 0:
        return 110.0
    if hours_remaining <= 24:
        return 95.0
    if hours_remaining <= 48:
        return 80.0
    if hours_remaining <= 72:
        return 65.0
    return 35.0