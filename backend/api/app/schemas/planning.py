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