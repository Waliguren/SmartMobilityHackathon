from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IncidenceCreate(BaseModel):
    contract_id: int | None = None
    charger_id: int | None = None
    planner_id: int | None = None
    priority: str = "normal"
    urgency_level: str = "medium"
    client_impact_score: int = 50
    auto_create_visit: bool = True
    due_at: datetime | None = None
    summary: str
    description: str | None = None
    zone_snapshot: str
    address_snapshot: str | None = None
    postal_code_snapshot: str | None = None
    latitude: float
    longitude: float
    estimated_duration_minutes: int = 60


class IncidenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contract_id: int | None
    charger_id: int | None
    planner_id: int | None
    status: str
    priority: str
    urgency_level: str
    client_impact_score: int
    auto_create_visit: bool
    created_at: datetime
    due_at: datetime | None
    summary: str
    description: str | None
    zone_snapshot: str
    address_snapshot: str | None
    postal_code_snapshot: str | None
    latitude: float
    longitude: float