from datetime import date, datetime

from pydantic import BaseModel


class WeeklyPlanningRequest(BaseModel):
    week_start_date: date
    technician_ids: list[int] | None = None
    max_assignment_radius_km: float | None = None
    use_google_fleet: bool = True
    fallback_to_a_star: bool = True
    publish: bool = False


class PlannedStop(BaseModel):
    visit_id: int
    incidence_id: int | None
    service_day: date
    sequence: int
    planned_arrival_at: datetime | None
    planned_departure_at: datetime | None
    travel_distance_km: float
    travel_minutes: int
    heuristic_score: float


class TechnicianWeeklyPlan(BaseModel):
    technician_id: int
    technician_name: str
    zone: str
    route_plan_id: int
    engine: str
    total_distance_km: float
    total_travel_minutes: int
    stops: list[PlannedStop]


class WeeklyPlanningResponse(BaseModel):
    engine: str
    week_start_date: date
    generated_plans: list[TechnicianWeeklyPlan]
    unassigned_visit_ids: list[int]
    message: str


class AiAssistantTaskInput(BaseModel):
    visit_id: str
    title: str
    address: str
    status: str
    visit_type: str
    priority: str
    client: str
    contract_type: str
    estimated_minutes: int = 60
    description: str | None = None
    created_at: datetime | None = None
    planned_date: datetime | None = None


class AiAssistantPlanningRequest(BaseModel):
    week_start_date: date
    technician_id: str
    technician_name: str
    technician_zone: str | None = None
    tasks: list[AiAssistantTaskInput]


class AiAssistantScheduledTask(BaseModel):
    visit_id: str
    title: str
    client: str
    address: str
    contract_type: str
    weekday: str
    start_time: str
    end_time: str
    priority_score: float
    reason: str


class AiAssistantPlanningResponse(BaseModel):
    engine: str
    summary: str
    preferences_assumed: list[str]
    used_fallback: bool = False
    scheduled_tasks: list[AiAssistantScheduledTask]
