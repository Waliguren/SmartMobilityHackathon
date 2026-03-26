from __future__ import annotations

from datetime import date, datetime, time
from enum import StrEnum

from sqlalchemy import Boolean
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Time
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base import Base


class IncidenceStatus(StrEnum):
    OPEN = "open"
    TRIAGED = "triaged"
    PLANNED = "planned"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"


class VisitStatus(StrEnum):
    PENDING = "pending"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class RoutePlanStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    impact_weight: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Charger(Base):
    __tablename__ = "chargers"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_ref: Mapped[str | None] = mapped_column(String(255))
    open_charge_map_id: Mapped[int | None] = mapped_column(Integer)
    name: Mapped[str | None] = mapped_column(String(255))
    zone: Mapped[str] = mapped_column(String(120), nullable=False)
    address: Mapped[str | None] = mapped_column(String(255))
    postal_code: Mapped[str | None] = mapped_column(String(32))
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    charger_id: Mapped[int] = mapped_column(ForeignKey("chargers.id"), nullable=False)
    domain_id: Mapped[int | None] = mapped_column(Integer)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    number_of_visits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    frequency: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    sla_priority: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    response_time_hours: Mapped[int | None] = mapped_column(Integer)
    resolution_time_hours: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    client: Mapped[Client] = relationship()
    charger: Mapped[Charger] = relationship()


class Technician(Base):
    __tablename__ = "technicians"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    zone: Mapped[str] = mapped_column(String(120), nullable=False)
    base_latitude: Mapped[float] = mapped_column(Float, nullable=False)
    base_longitude: Mapped[float] = mapped_column(Float, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    availabilities: Mapped[list[TechnicianAvailability]] = relationship(back_populates="technician")


class TechnicianAvailability(Base):
    __tablename__ = "technician_availabilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    technician_id: Mapped[int] = mapped_column(ForeignKey("technicians.id"), nullable=False)
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)
    available_from: Mapped[time] = mapped_column(Time, nullable=False)
    available_to: Mapped[time] = mapped_column(Time, nullable=False)
    capacity_minutes: Mapped[int] = mapped_column(Integer, default=480, nullable=False)

    technician: Mapped[Technician] = relationship(back_populates="availabilities")


class Incidence(Base):
    __tablename__ = "incidences"

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int | None] = mapped_column(ForeignKey("contracts.id"))
    charger_id: Mapped[int | None] = mapped_column(ForeignKey("chargers.id"))
    planner_id: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(50), default=IncidenceStatus.OPEN, nullable=False)
    priority: Mapped[str] = mapped_column(String(50), default="normal", nullable=False)
    urgency_level: Mapped[str] = mapped_column(String(50), default="medium", nullable=False)
    client_impact_score: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    auto_create_visit: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    summary: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    zone_snapshot: Mapped[str] = mapped_column(String(120), nullable=False)
    address_snapshot: Mapped[str | None] = mapped_column(String(255))
    postal_code_snapshot: Mapped[str | None] = mapped_column(String(32))
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    contract: Mapped[Contract | None] = relationship()
    charger: Mapped[Charger | None] = relationship()


class RoutePlan(Base):
    __tablename__ = "route_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    technician_id: Mapped[int] = mapped_column(ForeignKey("technicians.id"), nullable=False)
    week_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=RoutePlanStatus.DRAFT, nullable=False)
    source_engine: Mapped[str] = mapped_column(String(80), default="heuristic_a_star", nullable=False)
    total_distance_km: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_travel_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    technician: Mapped[Technician] = relationship()
    stops: Mapped[list[RouteStop]] = relationship(back_populates="route_plan")


class Visit(Base):
    __tablename__ = "visits"

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int | None] = mapped_column(ForeignKey("contracts.id"))
    incidence_id: Mapped[int | None] = mapped_column(ForeignKey("incidences.id"))
    technician_id: Mapped[int | None] = mapped_column(ForeignKey("technicians.id"))
    route_plan_id: Mapped[int | None] = mapped_column(ForeignKey("route_plans.id"))
    visit_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=VisitStatus.PENDING, nullable=False)
    planned_start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    planned_end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    zone_snapshot: Mapped[str] = mapped_column(String(120), nullable=False)
    address: Mapped[str | None] = mapped_column(String(255))
    postal_code: Mapped[str | None] = mapped_column(String(32))
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_duration_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    travel_minutes: Mapped[int | None] = mapped_column(Integer)
    heuristic_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    assignment_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    contract: Mapped[Contract | None] = relationship()
    incidence: Mapped[Incidence | None] = relationship()
    technician: Mapped[Technician | None] = relationship()
    route_plan: Mapped[RoutePlan | None] = relationship()
    report: Mapped[Report | None] = relationship(back_populates="visit")


class RouteStop(Base):
    __tablename__ = "route_stops"

    id: Mapped[int] = mapped_column(primary_key=True)
    route_plan_id: Mapped[int] = mapped_column(ForeignKey("route_plans.id"), nullable=False)
    visit_id: Mapped[int] = mapped_column(ForeignKey("visits.id"), nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    service_day: Mapped[date] = mapped_column(Date, nullable=False)
    planned_arrival_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    planned_departure_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    travel_distance_km: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    travel_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    route_plan: Mapped[RoutePlan] = relationship(back_populates="stops")
    visit: Mapped[Visit] = relationship()


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    visit_id: Mapped[int] = mapped_column(ForeignKey("visits.id"), nullable=False, unique=True)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    visit: Mapped[Visit] = relationship(back_populates="report")