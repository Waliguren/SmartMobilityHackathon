from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.models.entities import Technician
from app.schemas.technician import TechnicianCreate, TechnicianRead


router = APIRouter()


@router.get("", response_model=list[TechnicianRead])
def list_technicians(db: Session = Depends(get_db_session)) -> list[Technician]:
    return list(db.scalars(select(Technician).order_by(Technician.id)))


@router.post("", response_model=TechnicianRead, status_code=201)
def create_technician(
    payload: TechnicianCreate,
    db: Session = Depends(get_db_session),
) -> Technician:
    technician = Technician(**payload.model_dump())
    db.add(technician)
    db.commit()
    db.refresh(technician)
    return technician