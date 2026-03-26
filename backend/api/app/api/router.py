from fastapi import APIRouter

from app.api.routes.chargers import router as chargers_router
from app.api.routes.clients import router as clients_router
from app.api.routes.contracts import router as contracts_router
from app.api.routes.health import router as health_router
from app.api.routes.incidences import router as incidences_router
from app.api.routes.integrations import router as integrations_router
from app.api.routes.planning import router as planning_router
from app.api.routes.technicians import router as technicians_router
from app.api.routes.visits import router as visits_router


api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(clients_router, prefix="/clients", tags=["clients"])
api_router.include_router(chargers_router, prefix="/chargers", tags=["chargers"])
api_router.include_router(contracts_router, prefix="/contracts", tags=["contracts"])
api_router.include_router(technicians_router, prefix="/technicians", tags=["technicians"])
api_router.include_router(incidences_router, prefix="/incidences", tags=["incidences"])
api_router.include_router(visits_router, prefix="/visits", tags=["visits"])
api_router.include_router(planning_router, prefix="/planning", tags=["planning"])
api_router.include_router(integrations_router, prefix="/integrations", tags=["integrations"])