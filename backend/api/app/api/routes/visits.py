from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.models.entities import Visit
from app.schemas.visit import VisitRead


router = APIRouter()


@router.get("", response_model=list[VisitRead])
def list_visits(db: Session = Depends(get_db_session)) -> list[Visit]:
    return list(db.scalars(select(Visit).order_by(Visit.id)))