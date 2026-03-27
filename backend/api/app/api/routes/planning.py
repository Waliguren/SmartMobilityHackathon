from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db_session
from app.schemas.planning import AiAssistantPlanningRequest
from app.schemas.planning import AiAssistantPlanningResponse
from app.schemas.planning import WeeklyPlanningRequest, WeeklyPlanningResponse
from app.services.planning.ai_assistant_planner import AiAssistantPlanner
from app.services.planning.planner import WeeklyPlanner


router = APIRouter()


@router.post("/weekly-plan", response_model=WeeklyPlanningResponse)
def generate_weekly_plan(
    payload: WeeklyPlanningRequest,
    db: Session = Depends(get_db_session),
) -> WeeklyPlanningResponse:
    planner = WeeklyPlanner(db)
    return planner.generate_weekly_plan(payload)


@router.post("/ai-weekly-plan", response_model=AiAssistantPlanningResponse)
def generate_ai_weekly_plan(
    payload: AiAssistantPlanningRequest,
) -> AiAssistantPlanningResponse:
    planner = AiAssistantPlanner(get_settings())
    return planner.generate_weekly_plan(payload)
