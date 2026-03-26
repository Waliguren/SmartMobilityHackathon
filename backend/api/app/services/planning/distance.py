from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

import networkx as nx

from app.core.config import get_settings


def haversine_km(origin: tuple[float, float], destination: tuple[float, float]) -> float:
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius_km = 6371.0

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius_km * c


class RoadGraphDistanceService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.graph = self._load_graph()

    @property
    def has_graph(self) -> bool:
        return self.graph is not None and self.graph.number_of_nodes() > 0

    def distance_km(self, origin: tuple[float, float], destination: tuple[float, float]) -> float:
        if not self.has_graph:
            return haversine_km(origin, destination)

        start = self._nearest_node(origin)
        end = self._nearest_node(destination)
        if start is None or end is None:
            return haversine_km(origin, destination)

        try:
            return nx.astar_path_length(
                self.graph,
                start,
                end,
                heuristic=lambda left, right: haversine_km(left, right),
                weight="distance_km",
            )
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return haversine_km(origin, destination)

    def estimate_travel_minutes(self, distance_km: float) -> int:
        speed = max(self.settings.planning_average_speed_kph, 1.0)
        return int((distance_km / speed) * 60)

    def _nearest_node(self, point: tuple[float, float]) -> tuple[float, float] | None:
        if not self.has_graph:
            return None
        return min(self.graph.nodes, key=lambda candidate: haversine_km(point, candidate))

    @lru_cache(maxsize=1)
    def _load_graph(self) -> nx.Graph | None:
        path = self.settings.road_graph_geojson_path
        if not path:
            return None

        geojson_path = Path(path)
        if not geojson_path.exists():
            return None

        with geojson_path.open(encoding="utf-8") as handle:
            payload = json.load(handle)

        graph = nx.Graph()
        for feature in payload.get("features", []):
            geometry = feature.get("geometry", {})
            if geometry.get("type") != "LineString":
                continue

            coordinates = geometry.get("coordinates", [])
            points = [(coord[1], coord[0]) for coord in coordinates if len(coord) >= 2]
            for left, right in zip(points, points[1:]):
                graph.add_edge(left, right, distance_km=haversine_km(left, right))

        return graph