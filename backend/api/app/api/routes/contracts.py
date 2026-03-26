from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.models.entities import Contract
from app.schemas.contract import ContractCreate, ContractRead


router = APIRouter()


@router.get("", response_model=list[ContractRead])
def list_contracts(db: Session = Depends(get_db_session)) -> list[Contract]:
    return list(db.scalars(select(Contract).order_by(Contract.id)))


@router.post("", response_model=ContractRead, status_code=201)
def create_contract(payload: ContractCreate, db: Session = Depends(get_db_session)) -> Contract:
    contract = Contract(**payload.model_dump())
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract