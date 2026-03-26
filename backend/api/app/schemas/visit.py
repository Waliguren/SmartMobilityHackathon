from datetime import datetime

from pydantic import BaseModel, ConfigDict


class VisitRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contract_id: int | None
    incidence_id: int | None
    technician_id: int | None
    route_plan_id: int | None
    visit_type: str
    status: str
    planned_start_at: datetime | None
    planned_end_at: datetime | None
    due_at: datetime | None
    zone_snapshot: str
    address: str | None
    postal_code: str | None
    latitude: float
    longitude: float
    estimated_duration_minutes: int
    travel_minutes: int | None
    heuristic_score: float
    assignment_locked: bool