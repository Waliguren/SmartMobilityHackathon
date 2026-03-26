from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TechnicianCreate(BaseModel):
    name: str
    zone: str
    base_latitude: float
    base_longitude: float
    active: bool = True


class TechnicianRead(TechnicianCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime