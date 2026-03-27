from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

import httpx

from app.core.config import Settings
from app.schemas.planning import AiAssistantPlanningRequest
from app.schemas.planning import AiAssistantPlanningResponse
from app.schemas.planning import AiAssistantScheduledTask
from app.schemas.planning import AiAssistantTaskInput


DAY_ORDER = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
}

PREFERENCES_ASSUMED = [
    "Martes de 12:30 a 14:30 comida personal bloqueada.",
    "Jueves a partir de las 16:00 partido y no se programan visitas en esa franja.",
    "Horario laboral operativo de lunes a viernes, de 09:00 a 13:00 y de 15:00 a 18:00.",
]


@dataclass
class _ScoredTask:
    task: AiAssistantTaskInput
    score: float
    reason: str


@dataclass
class _Window:
    weekday: str
    start: datetime
    end: datetime


class AiAssistantPlanner:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.api_key = settings.groq_api_key or settings.grok_api_key

    def generate_weekly_plan(
        self,
        payload: AiAssistantPlanningRequest,
    ) -> AiAssistantPlanningResponse:
        if not payload.tasks:
            return AiAssistantPlanningResponse(
                engine="mock-groq-planner",
                summary="No hay tareas pendientes para planificar esta semana.",
                preferences_assumed=PREFERENCES_ASSUMED,
                used_fallback=False,
                scheduled_tasks=[],
            )

        week_start = payload.week_start_date - timedelta(
            days=payload.week_start_date.weekday(),
        )
        scored_tasks = self._score_tasks(payload.tasks)
        heuristic_schedule = self._build_heuristic_schedule(week_start, scored_tasks)
        heuristic_map = {item.visit_id: item for item in heuristic_schedule}

        if not self.api_key:
            return AiAssistantPlanningResponse(
                engine="heuristic-fallback",
                summary=(
                    "Plan generado con priorización heurística porque no se encontró "
                    "la clave de Groq/Grok en el entorno del backend."
                ),
                preferences_assumed=PREFERENCES_ASSUMED,
                used_fallback=True,
                scheduled_tasks=heuristic_schedule,
            )

        ai_result = self._request_groq_plan(payload, scored_tasks)
        if ai_result is None:
            return AiAssistantPlanningResponse(
                engine="heuristic-fallback",
                summary=(
                    "Plan generado con priorización heurística porque la respuesta "
                    "del agente Groq no fue válida."
                ),
                preferences_assumed=PREFERENCES_ASSUMED,
                used_fallback=True,
                scheduled_tasks=heuristic_schedule,
            )

        normalized_schedule, partial_fallback = self._normalize_ai_schedule(
            ai_result.get("scheduled_tasks"),
            scored_tasks,
            heuristic_map,
        )
        if not normalized_schedule:
            return AiAssistantPlanningResponse(
                engine="heuristic-fallback",
                summary=(
                    "Plan generado con priorización heurística porque no se pudo "
                    "normalizar la propuesta del agente Groq."
                ),
                preferences_assumed=PREFERENCES_ASSUMED,
                used_fallback=True,
                scheduled_tasks=heuristic_schedule,
            )

        summary = str(ai_result.get("summary") or "").strip()
        if not summary:
            summary = (
                "La IA ha ordenado la semana priorizando incidencias criticas, "
                "clientes premium y ventanas compatibles con la agenda personal."
            )

        return AiAssistantPlanningResponse(
            engine="groq-ai-assistant",
            summary=summary,
            preferences_assumed=PREFERENCES_ASSUMED,
            used_fallback=partial_fallback,
            scheduled_tasks=normalized_schedule,
        )

    def _request_groq_plan(
        self,
        payload: AiAssistantPlanningRequest,
        scored_tasks: list[_ScoredTask],
    ) -> dict | None:
        task_lines = []
        for item in scored_tasks:
            task_lines.append(
                json.dumps(
                    {
                        "visit_id": item.task.visit_id,
                        "title": item.task.title,
                        "client": item.task.client,
                        "address": item.task.address,
                        "contract_type": item.task.contract_type,
                        "priority": item.task.priority,
                        "visit_type": item.task.visit_type,
                        "status": item.task.status,
                        "estimated_minutes": item.task.estimated_minutes,
                        "priority_score": round(item.score, 1),
                        "heuristic_reason": item.reason,
                    },
                    ensure_ascii=False,
                ),
            )

        system_prompt = (
            "Eres un agente experto en planificación semanal de técnicos de campo "
            "para estaciones de carga. Debes devolver solo JSON válido."
        )
        user_prompt = f"""
Genera el planning semanal para el técnico {payload.technician_name} ({payload.technician_id}) de la zona {payload.technician_zone or 'sin zona'}.

Preferencias personales mockeadas del calendario:
- Martes de 12:30 a 14:30 tiene una comida y no puede aceptar tareas ahí.
- Jueves a partir de las 16:00 tiene partido y se bloquea toda la tarde restante.
- Horario base: lunes a viernes de 09:00 a 13:00 y de 15:00 a 18:00.

Reglas de negocio obligatorias:
1. La prioridad principal es resolver antes las tareas más críticas.
2. El SLA manda: el cliente que más paga tiene más prioridad.
3. Las averías y prioridades altas deben quedar antes que mantenimientos menos críticos.
4. Respeta las preferencias personales del técnico.
5. Devuelve todas las tareas programadas una sola vez.
6. Ordena la respuesta de lunes a viernes, de arriba a abajo.
7. Si dudas, conserva el orden sugerido por priority_score.

Semana que empieza el: {payload.week_start_date.isoformat()}

Tareas ya preordenadas por criticidad:
{chr(10).join(task_lines)}

Devuelve este JSON exacto:
{{
  "summary": "resumen breve en español",
  "scheduled_tasks": [
    {{
      "visit_id": "V_01",
      "weekday": "monday",
      "start_time": "09:00",
      "end_time": "10:30",
      "reason": "motivo breve en español"
    }}
  ]
}}
"""

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": 0.2,
                        "max_tokens": 1800,
                    },
                )
                response.raise_for_status()
        except httpx.HTTPError:
            return None

        try:
            content = response.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, ValueError):
            return None

        return self._extract_json(content)

    def _extract_json(self, raw_content: str) -> dict | None:
        content = raw_content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start < 0 or end <= start:
                return None
            try:
                return json.loads(content[start:end])
            except json.JSONDecodeError:
                return None

    def _normalize_ai_schedule(
        self,
        raw_items: object,
        scored_tasks: list[_ScoredTask],
        heuristic_map: dict[str, AiAssistantScheduledTask],
    ) -> tuple[list[AiAssistantScheduledTask], bool]:
        if not isinstance(raw_items, list):
            return [], True

        score_lookup = {item.task.visit_id: item for item in scored_tasks}
        scheduled: list[AiAssistantScheduledTask] = []
        seen: set[str] = set()

        for raw_item in raw_items:
            if not isinstance(raw_item, dict):
                continue

            visit_id = str(raw_item.get("visit_id") or "").strip()
            if not visit_id or visit_id in seen or visit_id not in score_lookup:
                continue

            weekday = self._normalize_weekday(raw_item.get("weekday"))
            start_time = self._normalize_time(raw_item.get("start_time"))
            end_time = self._normalize_time(raw_item.get("end_time"))
            if weekday is None or start_time is None or end_time is None:
                continue

            scored = score_lookup[visit_id]
            scheduled.append(
                AiAssistantScheduledTask(
                    visit_id=visit_id,
                    title=scored.task.title,
                    client=scored.task.client,
                    address=scored.task.address,
                    contract_type=scored.task.contract_type,
                    weekday=weekday,
                    start_time=start_time,
                    end_time=end_time,
                    priority_score=round(scored.score, 1),
                    reason=str(raw_item.get("reason") or scored.reason).strip(),
                ),
            )
            seen.add(visit_id)

        partial_fallback = False
        for visit_id, heuristic_item in heuristic_map.items():
            if visit_id in seen:
                continue
            partial_fallback = True
            scheduled.append(heuristic_item)

        scheduled.sort(key=self._scheduled_sort_key)
        return scheduled, partial_fallback

    def _build_heuristic_schedule(
        self,
        week_start: date,
        scored_tasks: list[_ScoredTask],
    ) -> list[AiAssistantScheduledTask]:
        windows = self._build_windows(week_start)
        scheduled: list[AiAssistantScheduledTask] = []
        overflow_cursor = datetime.combine(week_start + timedelta(days=4), time(15, 0))

        for scored in scored_tasks:
            duration_minutes = max(45, min(scored.task.estimated_minutes, 180))
            slot = self._allocate_slot(windows, duration_minutes)
            if slot is None:
                start_dt = overflow_cursor
                end_dt = start_dt + timedelta(minutes=duration_minutes)
                overflow_cursor = end_dt + timedelta(minutes=15)
                weekday = "friday"
            else:
                weekday, start_dt, end_dt = slot

            scheduled.append(
                AiAssistantScheduledTask(
                    visit_id=scored.task.visit_id,
                    title=scored.task.title,
                    client=scored.task.client,
                    address=scored.task.address,
                    contract_type=scored.task.contract_type,
                    weekday=weekday,
                    start_time=start_dt.strftime("%H:%M"),
                    end_time=end_dt.strftime("%H:%M"),
                    priority_score=round(scored.score, 1),
                    reason=scored.reason,
                ),
            )

        scheduled.sort(key=self._scheduled_sort_key)
        return scheduled

    def _allocate_slot(
        self,
        windows: list[_Window],
        duration_minutes: int,
    ) -> tuple[str, datetime, datetime] | None:
        duration = timedelta(minutes=duration_minutes)
        travel_buffer = timedelta(minutes=15)

        for window in windows:
            if window.end - window.start < duration:
                continue

            start_dt = window.start
            end_dt = start_dt + duration
            window.start = end_dt + travel_buffer
            return window.weekday, start_dt, end_dt

        return None

    def _build_windows(self, week_start: date) -> list[_Window]:
        blocks = [
            ("monday", time(9, 0), time(13, 0)),
            ("monday", time(15, 0), time(18, 0)),
            ("tuesday", time(9, 0), time(12, 30)),
            ("tuesday", time(14, 30), time(18, 0)),
            ("wednesday", time(9, 0), time(13, 0)),
            ("wednesday", time(15, 0), time(18, 0)),
            ("thursday", time(9, 0), time(13, 0)),
            ("thursday", time(15, 0), time(16, 0)),
            ("friday", time(9, 0), time(13, 0)),
            ("friday", time(15, 0), time(18, 0)),
        ]

        windows: list[_Window] = []
        for weekday, start_time, end_time in blocks:
            day_date = week_start + timedelta(days=DAY_ORDER[weekday])
            windows.append(
                _Window(
                    weekday=weekday,
                    start=datetime.combine(day_date, start_time),
                    end=datetime.combine(day_date, end_time),
                ),
            )
        return windows

    def _score_tasks(self, tasks: list[AiAssistantTaskInput]) -> list[_ScoredTask]:
        scored_tasks: list[_ScoredTask] = []
        for task in tasks:
            contract_score = self._contract_score(task.contract_type)
            severity_score = self._severity_score(task.priority)
            visit_type_score = self._visit_type_score(task.visit_type)
            status_score = self._status_score(task.status)
            age_score = self._age_score(task.created_at)

            weighted_score = (
                (contract_score * 0.40)
                + (severity_score * 0.25)
                + (visit_type_score * 0.15)
                + (status_score * 0.10)
                + (age_score * 0.10)
            )

            reason = (
                f"Se prioriza por SLA/cliente ({task.contract_type}), "
                f"criticidad {task.priority} y tipo de visita {task.visit_type}."
            )

            scored_tasks.append(
                _ScoredTask(
                    task=task,
                    score=weighted_score,
                    reason=reason,
                ),
            )

        scored_tasks.sort(key=lambda item: (-item.score, item.task.planned_date or datetime.max))
        return scored_tasks

    def _contract_score(self, contract_type: str) -> float:
        contract = contract_type.lower()
        if "premium" in contract:
            return 100.0
        if "or" in contract or "gold" in contract or "oro" in contract:
            return 88.0
        if "basic" in contract or "bàsic" in contract or "basic" in contract:
            return 55.0
        return 70.0

    def _severity_score(self, priority: str) -> float:
        normalized = priority.lower()
        if normalized in {"critical", "critica", "crítica", "alta", "high", "urgent", "urgente"}:
            return 100.0
        if normalized in {"mitja", "media", "medium", "normal"}:
            return 72.0
        return 45.0

    def _visit_type_score(self, visit_type: str) -> float:
        normalized = visit_type.lower()
        if normalized in {"avaria", "corrective", "correctivo", "incidencia"}:
            return 100.0
        return 60.0

    def _status_score(self, status: str) -> float:
        normalized = status.lower()
        if normalized in {"en_curs", "in_progress", "in progress"}:
            return 90.0
        if normalized in {"pendent", "pendiente", "pending"}:
            return 75.0
        return 40.0

    def _age_score(self, created_at: datetime | None) -> float:
        if created_at is None:
            return 55.0
        elapsed_hours = max((datetime.utcnow() - created_at).total_seconds() / 3600, 0)
        return min(100.0, 55.0 + (elapsed_hours / 6.0))

    def _normalize_weekday(self, raw_value: object) -> str | None:
        normalized = str(raw_value or "").strip().lower()
        aliases = {
            "lunes": "monday",
            "monday": "monday",
            "martes": "tuesday",
            "tuesday": "tuesday",
            "miercoles": "wednesday",
            "miércoles": "wednesday",
            "wednesday": "wednesday",
            "jueves": "thursday",
            "thursday": "thursday",
            "viernes": "friday",
            "friday": "friday",
        }
        return aliases.get(normalized)

    def _normalize_time(self, raw_value: object) -> str | None:
        text = str(raw_value or "").strip()
        if len(text) < 4 or ":" not in text:
            return None
        hour_part, minute_part = text.split(":", 1)
        if not hour_part.isdigit() or not minute_part[:2].isdigit():
            return None
        hour = int(hour_part)
        minute = int(minute_part[:2])
        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
            return None
        return f"{hour:02d}:{minute:02d}"

    def _scheduled_sort_key(
        self,
        item: AiAssistantScheduledTask,
    ) -> tuple[int, str, str]:
        return (
            DAY_ORDER.get(item.weekday.lower(), 99),
            item.start_time,
            item.visit_id,
        )
