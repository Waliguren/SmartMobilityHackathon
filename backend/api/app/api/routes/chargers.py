from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.models.entities import Charger
from app.schemas.charger import ChargerCreate, ChargerRead


router = APIRouter()


@router.get("", response_model=list[ChargerRead])
def list_chargers(db: Session = Depends(get_db_session)) -> list[Charger]:
    return list(db.scalars(select(Charger).order_by(Charger.id)))


@router.post("", response_model=ChargerRead, status_code=201)
def create_charger(payload: ChargerCreate, db: Session = Depends(get_db_session)) -> Charger:
    charger = Charger(**payload.model_dump())
    db.add(charger)
    db.commit()
    db.refresh(charger)
    return charger