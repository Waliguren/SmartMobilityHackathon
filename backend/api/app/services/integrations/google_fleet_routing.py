import json

import httpx
from google.auth.transport.requests import Request
from google.oauth2 import service_account

from app.core.config import get_settings


FLEET_ROUTING_SCOPE = ["https://www.googleapis.com/auth/cloud-platform"]


class GoogleFleetRoutingClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def is_configured(self) -> bool:
        return bool(
            self.settings.google_cloud_project_id
            and (
                self.settings.google_service_account_file
                or self.settings.google_service_account_json
            )
        )

    def optimize_tours(self, shipment_model: dict) -> dict:
        if not self.is_configured:
            raise RuntimeError("Google Fleet Routing no está configurado")

        credentials = self._build_credentials()
        credentials.refresh(Request())

        project = self.settings.google_cloud_project_id
        location = self.settings.google_cloud_location
        url = f"https://fleetrouting.googleapis.com/v1/projects/{project}/locations/{location}:optimizeTours"
        headers = {"Authorization": f"Bearer {credentials.token}"}

        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, headers=headers, json=shipment_model)
            response.raise_for_status()
            return response.json()

    def _build_credentials(self):
        if self.settings.google_service_account_file:
            return service_account.Credentials.from_service_account_file(
                self.settings.google_service_account_file,
                scopes=FLEET_ROUTING_SCOPE,
            )

        return service_account.Credentials.from_service_account_info(
            json.loads(self.settings.google_service_account_json or "{}"),
            scopes=FLEET_ROUTING_SCOPE,
        )