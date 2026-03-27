from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Smart Mobility API"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    database_url: str = "postgresql+psycopg://smartmobility:smartmobility@localhost:5432/smartmobility"
    database_auto_create: bool = True
    database_echo: bool = False

    planning_default_daily_capacity_minutes: int = 480
    planning_max_assignment_radius_km: float = 180.0
    planning_average_speed_kph: float = 60.0
    road_graph_geojson_path: str | None = None

    firebase_project_id: str | None = None
    firebase_client_email: str | None = None
    firebase_private_key: str | None = None
    firebase_storage_bucket: str | None = None

    openchargemap_api_key: str | None = None
    openchargemap_base_url: str = "https://api.openchargemap.io/v3"

    groq_api_key: str | None = None
    grok_api_key: str | None = None

    google_cloud_project_id: str | None = None
    google_cloud_location: str = "global"
    google_service_account_file: str | None = None
    google_service_account_json: str | None = None
    google_fleet_routing_enabled: bool = False

    @field_validator("api_cors_origins", mode="before")
    @classmethod
    def _parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        if not value:
            return ["*"]
        return [origin.strip() for origin in value.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
