from fastapi import APIRouter

from app.core.config import get_settings
from app.services.integrations.google_fleet_routing import GoogleFleetRoutingClient
from app.services.integrations.openchargemap import OpenChargeMapClient


router = APIRouter()


@router.get("/openchargemap/health")
def openchargemap_health() -> dict[str, bool | str]:
    client = OpenChargeMapClient()
    return {
        "integration": "openchargemap",
        "configured": client.is_configured,
        "base_url": client.base_url,
    }


@router.get("/fleet-routing/health")
def fleet_routing_health() -> dict[str, bool | str]:
    settings = get_settings()
    client = GoogleFleetRoutingClient()
    return {
        "integration": "google_fleet_routing",
        "enabled": settings.google_fleet_routing_enabled,
        "configured": client.is_configured,
        "location": settings.google_cloud_location,
    }