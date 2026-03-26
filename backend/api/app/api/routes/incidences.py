from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.models.entities import Incidence, Visit, VisitStatus
from app.schemas.incidence import IncidenceCreate, IncidenceRead


router = APIRouter()


@router.get("", response_model=list[IncidenceRead])
def list_incidences(db: Session = Depends(get_db_session)) -> list[Incidence]:
    return list(db.scalars(select(Incidence).order_by(Incidence.created_at.desc())))


@router.post("", response_model=IncidenceRead, status_code=201)
def create_incidence(
    payload: IncidenceCreate,
    db: Session = Depends(get_db_session),
) -> Incidence:
    incidence = Incidence(**payload.model_dump())
    db.add(incidence)
    db.flush()

    if incidence.auto_create_visit:
        visit = Visit(
            contract_id=incidence.contract_id,
            incidence_id=incidence.id,
            visit_type="corrective",
            status=VisitStatus.PENDING,
            due_at=incidence.due_at,
            zone_snapshot=incidence.zone_snapshot,
            address=incidence.address_snapshot,
            postal_code=incidence.postal_code_snapshot,
            latitude=incidence.latitude,
            longitude=incidence.longitude,
            estimated_duration_minutes=payload.estimated_duration_minutes,
        )
        db.add(visit)

    db.commit()
    db.refresh(incidence)
    return incidence