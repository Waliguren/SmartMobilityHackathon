from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChargerCreate(BaseModel):
    external_ref: str | None = None
    open_charge_map_id: int | None = None
    name: str | None = None
    zone: str
    address: str | None = None
    postal_code: str | None = None
    latitude: float
    longitude: float


class ChargerRead(ChargerCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime