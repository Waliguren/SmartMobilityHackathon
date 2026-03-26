from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ClientCreate(BaseModel):
    name: str
    impact_weight: int = 50


class ClientRead(ClientCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime