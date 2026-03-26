from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.planning import WeeklyPlanningRequest, WeeklyPlanningResponse
from app.services.planning.planner import WeeklyPlanner


router = APIRouter()


@router.post("/weekly-plan", response_model=WeeklyPlanningResponse)
def generate_weekly_plan(
    payload: WeeklyPlanningRequest,
    db: Session = Depends(get_db_session),
) -> WeeklyPlanningResponse:
    planner = WeeklyPlanner(db)
    return planner.generate_weekly_plan(payload)