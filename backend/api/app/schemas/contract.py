from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ContractCreate(BaseModel):
    type: str
    client_id: int
    charger_id: int
    domain_id: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    number_of_visits: int = 0
    frequency: str | None = None
    status: str = "active"
    sla_priority: int = 5
    response_time_hours: int | None = None
    resolution_time_hours: int | None = None


class ContractRead(ContractCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime