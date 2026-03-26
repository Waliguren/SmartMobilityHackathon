import httpx

from app.core.config import get_settings


class OpenChargeMapClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = settings.openchargemap_api_key
        self.base_url = settings.openchargemap_base_url.rstrip("/")

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def search_nearby(self, latitude: float, longitude: float, distance_km: float = 25.0) -> list[dict]:
        if not self.is_configured:
            return []

        params = {
            "key": self.api_key,
            "latitude": latitude,
            "longitude": longitude,
            "distance": distance_km,
            "distanceunit": "KM",
            "maxresults": 20,
        }
        with httpx.Client(timeout=15.0) as client:
            response = client.get(f"{self.base_url}/poi/", params=params)
            response.raise_for_status()
            return response.json()