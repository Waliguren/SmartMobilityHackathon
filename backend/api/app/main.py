from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine
from app.models.entities import Charger
from app.models.entities import Client
from app.models.entities import Contract
from app.models.entities import Incidence
from app.models.entities import Report
from app.models.entities import RoutePlan
from app.models.entities import RouteStop
from app.models.entities import Technician
from app.models.entities import TechnicianAvailability
from app.models.entities import Visit


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="Backend operativo para planificación de mantenimiento y routing semanal.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    if settings.database_auto_create:
        Base.metadata.create_all(bind=engine)


app.include_router(api_router, prefix=settings.api_v1_prefix)