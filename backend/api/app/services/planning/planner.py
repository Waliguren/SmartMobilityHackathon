from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta

from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.entities import Contract
from app.models.entities import Incidence
from app.models.entities import RoutePlan
from app.models.entities import RoutePlanStatus
from app.models.entities import RouteStop
from app.models.entities import Technician
from app.models.entities import TechnicianAvailability
from app.models.entities import Visit
from app.models.entities import VisitStatus
from app.schemas.planning import PlannedStop
from app.schemas.planning import TechnicianWeeklyPlan
from app.schemas.planning import WeeklyPlanningRequest
from app.schemas.planning import WeeklyPlanningResponse
from app.services.integrations.google_fleet_routing import GoogleFleetRoutingClient
from app.services.planning.distance import RoadGraphDistanceService
from app.services.planning.scoring import compute_visit_score


@dataclass
class DailyAssignment:
    service_day: date
    remaining_minutes: int
    current_position: tuple[float, float]
    current_time: datetime
    visits: list[Visit]


class WeeklyPlanner:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()
        self.distance_service = RoadGraphDistanceService()
        self.google_client = GoogleFleetRoutingClient()

    def generate_weekly_plan(self, payload: WeeklyPlanningRequest) -> WeeklyPlanningResponse:
        visits = self._candidate_visits()
        technicians = self._technicians(payload.technician_ids)
        if not visits or not technicians:
            return WeeklyPlanningResponse(
                engine="heuristic_a_star",
                week_start_date=payload.week_start_date,
                generated_plans=[],
                unassigned_visit_ids=[visit.id for visit in visits],
                message="No hay técnicos activos o visitas candidatas para planificar.",
            )

        engine_name = "heuristic_a_star"
        if payload.use_google_fleet and self.settings.google_fleet_routing_enabled and self.google_client.is_configured:
            engine_name = "google_fleet_routing_fallback"

        self._clear_existing_draft_plans(payload.week_start_date, technicians)
        assignments = self._build_week_assignments(payload.week_start_date, technicians)

        ordered_visits = sorted(
            visits,
            key=lambda visit: (-visit.heuristic_score, visit.due_at or datetime.max.replace(tzinfo=UTC)),
        )

        unassigned_visit_ids: list[int] = []
        for visit in ordered_visits:
            best_option = self._select_slot(assignments, visit, payload.max_assignment_radius_km)
            if best_option is None:
                unassigned_visit_ids.append(visit.id)
                continue

            technician_id, daily = best_option
            travel_km = self.distance_service.distance_km(
                daily.current_position,
                (visit.latitude, visit.longitude),
            )
            travel_minutes = self.distance_service.estimate_travel_minutes(travel_km)
            daily.remaining_minutes -= travel_minutes + visit.estimated_duration_minutes
            visit.travel_minutes = travel_minutes
            visit.technician_id = technician_id
            daily.current_position = (visit.latitude, visit.longitude)
            arrival = daily.current_time + timedelta(minutes=travel_minutes)
            departure = arrival + timedelta(minutes=visit.estimated_duration_minutes)
            visit.planned_start_at = arrival
            visit.planned_end_at = departure
            visit.status = VisitStatus.PLANNED
            daily.current_time = departure
            daily.visits.append(visit)

        generated_plans: list[TechnicianWeeklyPlan] = []
        for technician in technicians:
            route_plan = RoutePlan(
                technician_id=technician.id,
                week_start_date=payload.week_start_date,
                status=RoutePlanStatus.PUBLISHED if payload.publish else RoutePlanStatus.DRAFT,
                source_engine=engine_name,
            )
            self.db.add(route_plan)
            self.db.flush()

            stops: list[PlannedStop] = []
            sequence = 1
            total_distance_km = 0.0
            total_travel_minutes = 0

            for day_assignment in assignments[technician.id]:
                previous_position = (technician.base_latitude, technician.base_longitude)
                day_visits = self._nearest_neighbor_order(previous_position, day_assignment.visits)
                for visit in day_visits:
                    travel_km = self.distance_service.distance_km(previous_position, (visit.latitude, visit.longitude))
                    travel_minutes = self.distance_service.estimate_travel_minutes(travel_km)
                    previous_position = (visit.latitude, visit.longitude)

                    route_stop = RouteStop(
                        route_plan_id=route_plan.id,
                        visit_id=visit.id,
                        sequence=sequence,
                        service_day=day_assignment.service_day,
                        planned_arrival_at=visit.planned_start_at,
                        planned_departure_at=visit.planned_end_at,
                        travel_distance_km=travel_km,
                        travel_minutes=travel_minutes,
                    )
                    self.db.add(route_stop)

                    visit.route_plan_id = route_plan.id
                    total_distance_km += travel_km
                    total_travel_minutes += travel_minutes
                    stops.append(
                        PlannedStop(
                            visit_id=visit.id,
                            incidence_id=visit.incidence_id,
                            service_day=day_assignment.service_day,
                            sequence=sequence,
                            planned_arrival_at=visit.planned_start_at,
                            planned_departure_at=visit.planned_end_at,
                            travel_distance_km=round(travel_km, 2),
                            travel_minutes=travel_minutes,
                            heuristic_score=visit.heuristic_score,
                        )
                    )
                    sequence += 1

            route_plan.total_distance_km = round(total_distance_km, 2)
            route_plan.total_travel_minutes = total_travel_minutes
            generated_plans.append(
                TechnicianWeeklyPlan(
                    technician_id=technician.id,
                    technician_name=technician.name,
                    zone=technician.zone,
                    route_plan_id=route_plan.id,
                    engine=engine_name,
                    total_distance_km=route_plan.total_distance_km,
                    total_travel_minutes=route_plan.total_travel_minutes,
                    stops=stops,
                )
            )

        self.db.commit()
        return WeeklyPlanningResponse(
            engine=engine_name,
            week_start_date=payload.week_start_date,
            generated_plans=generated_plans,
            unassigned_visit_ids=unassigned_visit_ids,
            message="Plan semanal generado con heurística operativa y fallback local.",
        )

    def _candidate_visits(self) -> list[Visit]:
        visits = list(
            self.db.scalars(
                select(Visit)
                .where(Visit.status.in_([VisitStatus.PENDING, VisitStatus.PLANNED]))
                .where(Visit.assignment_locked.is_(False))
            )
        )

        incidence_by_id = {
            incidence.id: incidence
            for incidence in self.db.scalars(select(Incidence))
        }
        contract_by_id = {
            contract.id: contract
            for contract in self.db.scalars(select(Contract))
        }

        for visit in visits:
            incidence = incidence_by_id.get(visit.incidence_id)
            contract = contract_by_id.get(visit.contract_id)
            visit.heuristic_score = compute_visit_score(contract, incidence)
        return visits

    def _technicians(self, technician_ids: list[int] | None) -> list[Technician]:
        statement = select(Technician).where(Technician.active.is_(True))
        if technician_ids:
            statement = statement.where(Technician.id.in_(technician_ids))
        return list(self.db.scalars(statement.order_by(Technician.id)))

    def _build_week_assignments(self, week_start: date, technicians: list[Technician]) -> dict[int, list[DailyAssignment]]:
        availability_map = defaultdict(list)
        availability_rows = list(self.db.scalars(select(TechnicianAvailability)))
        for availability in availability_rows:
            availability_map[availability.technician_id].append(availability)

        assignments: dict[int, list[DailyAssignment]] = {}
        for technician in technicians:
            days: list[DailyAssignment] = []
            technician_availabilities = availability_map.get(technician.id)
            if technician_availabilities:
                for offset in range(7):
                    service_day = week_start + timedelta(days=offset)
                    weekday = service_day.weekday()
                    matching = next((item for item in technician_availabilities if item.weekday == weekday), None)
                    if matching is None:
                        continue
                    start_at = datetime.combine(service_day, matching.available_from, tzinfo=UTC)
                    days.append(
                        DailyAssignment(
                            service_day=service_day,
                            remaining_minutes=matching.capacity_minutes,
                            current_position=(technician.base_latitude, technician.base_longitude),
                            current_time=start_at,
                            visits=[],
                        )
                    )
            else:
                for offset in range(5):
                    service_day = week_start + timedelta(days=offset)
                    days.append(
                        DailyAssignment(
                            service_day=service_day,
                            remaining_minutes=self.settings.planning_default_daily_capacity_minutes,
                            current_position=(technician.base_latitude, technician.base_longitude),
                            current_time=datetime.combine(service_day, time(hour=8), tzinfo=UTC),
                            visits=[],
                        )
                    )

            assignments[technician.id] = days

        return assignments

    def _select_slot(
        self,
        assignments: dict[int, list[DailyAssignment]],
        visit: Visit,
        radius_override_km: float | None,
    ) -> tuple[int, DailyAssignment] | None:
        max_radius_km = radius_override_km or self.settings.planning_max_assignment_radius_km
        best: tuple[float, int, DailyAssignment] | None = None

        for technician_id, daily_slots in assignments.items():
            for daily in daily_slots:
                if visit.due_at and daily.service_day > visit.due_at.date():
                    continue

                travel_km = self.distance_service.distance_km(
                    daily.current_position,
                    (visit.latitude, visit.longitude),
                )
                if travel_km > max_radius_km:
                    continue

                required_minutes = self.distance_service.estimate_travel_minutes(travel_km) + visit.estimated_duration_minutes
                if required_minutes > daily.remaining_minutes:
                    continue

                zone_penalty = 0 if visit.zone_snapshot.lower() == self._technician_zone(assignments, technician_id).lower() else 15
                objective = travel_km + zone_penalty - (visit.heuristic_score * 0.1)
                if best is None or objective < best[0]:
                    best = (objective, technician_id, daily)

        if best is None:
            return None
        return best[1], best[2]

    def _technician_zone(self, assignments: dict[int, list[DailyAssignment]], technician_id: int) -> str:
        technician = self.db.get(Technician, technician_id)
        return technician.zone if technician else ""

    def _nearest_neighbor_order(self, start: tuple[float, float], visits: list[Visit]) -> list[Visit]:
        remaining = visits[:]
        ordered: list[Visit] = []
        current = start
        while remaining:
            next_visit = min(
                remaining,
                key=lambda visit: self.distance_service.distance_km(current, (visit.latitude, visit.longitude)),
            )
            ordered.append(next_visit)
            current = (next_visit.latitude, next_visit.longitude)
            remaining.remove(next_visit)
        return ordered

    def _clear_existing_draft_plans(self, week_start: date, technicians: list[Technician]) -> None:
        technician_ids = [technician.id for technician in technicians]
        if not technician_ids:
            return

        route_plan_ids = list(
            self.db.scalars(
                select(RoutePlan.id)
                .where(RoutePlan.week_start_date == week_start)
                .where(RoutePlan.technician_id.in_(technician_ids))
                .where(RoutePlan.status == RoutePlanStatus.DRAFT)
            )
        )
        if not route_plan_ids:
            return

        self.db.execute(
            update(Visit)
            .where(Visit.route_plan_id.in_(route_plan_ids))
            .values(route_plan_id=None)
        )
        self.db.execute(delete(RouteStop).where(RouteStop.route_plan_id.in_(route_plan_ids)))
        self.db.execute(delete(RoutePlan).where(RoutePlan.id.in_(route_plan_ids)))