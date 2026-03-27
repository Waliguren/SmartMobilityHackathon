import json
from datetime import UTC, datetime
from pathlib import Path

from src import bcrypt, db
from src.models.operations import Contract, Incidence, Report, Technician, Visit
from src.models.user import User

TYPE_LABELS = {
    "avaria": "Incidencia",
    "manteniment": "Mantenimiento",
    "puesta_marcha": "Puesta en marcha",
}

TYPE_KEYS = {
    "avaria": "incidencia",
    "manteniment": "mantenimiento",
    "puesta_marcha": "puesta_marcha",
}

PRIORITY_LABELS = {
    "alta": "Alta",
    "mitja": "Media",
    "baixa": "Baja",
}

PRIORITY_BADGES = {
    "alta": "danger",
    "mitja": "warning",
    "baixa": "secondary",
}

VISIT_STATUS_LABELS = {
    "pendent": "Pendiente",
    "en_curs": "En curso",
    "completada": "Completada",
}

VISIT_STATUS_BADGES = {
    "pendent": "warning",
    "en_curs": "primary",
    "completada": "success",
}

MAP_STATUS_LABELS = {
    "por_asignar": "Por asignar",
    "asignada": "Asignada",
    "resuelta": "Resuelta",
}

MAP_STATUS_BADGES = {
    "por_asignar": "secondary",
    "asignada": "primary",
    "resuelta": "success",
}

INCIDENCE_STATUS_LABELS = {
    "oberta": "Abierta",
    "en_proces": "En proceso",
    "tancada": "Cerrada",
}

INCIDENCE_STATUS_BADGES = {
    "oberta": "danger",
    "en_proces": "warning",
    "tancada": "success",
}

REPORT_STATUS_LABELS = {
    "firmat": "Firmado",
    "esborrany": "Borrador",
    "pendent": "Pendiente",
}

REPORT_STATUS_BADGES = {
    "firmat": "success",
    "esborrany": "warning",
    "pendent": "secondary",
}

RISK_RESPONSE_SLA_HOURS = {
    "alta": 4,
    "mitja": 8,
    "baixa": 24,
}


def ensure_operational_data(app):
    backup_path = Path(app.config["BACKUP_JSON_PATH"])
    _ensure_default_user()

    if not backup_path.exists():
        app.logger.warning("No se encontro backup JSON en %s", backup_path)
        return

    with backup_path.open("r", encoding="utf-8") as backup_file:
        payload = json.load(backup_file)

    db.session.query(Report).delete()
    db.session.query(Visit).delete()
    db.session.query(Incidence).delete()
    db.session.query(Contract).delete()
    db.session.query(Technician).delete()

    for item in payload.get("technicians", []):
        db.session.add(
            Technician(
                id=item["id"],
                name=item["name"],
                zone=item["zone"],
                expertise=item.get("expertice", item.get("expertise", 0)),
                expert=bool(item.get("expert", False)),
            )
        )

    for item in payload.get("contracts", []):
        latitude, longitude = _parse_location(item.get("location"))
        db.session.add(
            Contract(
                id=item["id"],
                client_id=item["client_id"],
                charger_id=item["charger_id"],
                contract_type=item["type"],
                address=item["address"],
                latitude=latitude,
                longitude=longitude,
                status=item["status"],
            )
        )

    for item in payload.get("incidences", []):
        db.session.add(
            Incidence(
                id=item["id"],
                charger_id=item["charger_id"],
                priority=item["priority"],
                status=item["status"],
                description=item["description"],
                created_at=_parse_timestamp(item.get("created_at")),
            )
        )

    for item in payload.get("visits", []):
        latitude, longitude = _parse_location(item.get("location"))
        db.session.add(
            Visit(
                id=item["id"],
                technician_id=item.get("technician_id"),
                incidence_id=item["incidence_id"],
                status=item["status"],
                visit_type=item["visit_type"],
                address=item["address"],
                latitude=latitude,
                longitude=longitude,
                planned_date=_parse_timestamp(item.get("planned_date")),
            )
        )

    for item in payload.get("reports", []):
        db.session.add(
            Report(
                id=item["id"],
                visit_id=item["visit_id"],
                technician_id=item["technician_id"],
                report_type=item["report_type"],
                status=item["status"],
                observations=item["observations"],
                created_at=_parse_timestamp(item.get("created_at")),
            )
        )

    db.session.commit()


def build_dashboard_context():
    tasks = list_task_cards()
    risks = list_risk_cards()
    technicians = list_technician_cards()

    return {
        "pending_tasks": len([task for task in tasks if task["status_key"] != "completada"]),
        "sla_risks": len(risks),
        "active_technicians": len(technicians),
        "completed_tasks": len([task for task in tasks if task["status_key"] == "completada"]),
        "priority_tasks": [task for task in tasks if task["priority_key"] == "alta" and task["status_key"] != "completada"][:5],
    }


def list_task_cards():
    contracts = {contract.charger_id: contract for contract in Contract.query.all()}
    visits = Visit.query.order_by(Visit.planned_date.asc(), Visit.id.asc()).all()
    return [_serialize_task(visit, contracts) for visit in visits]


def get_task_card(task_id):
    contracts = {contract.charger_id: contract for contract in Contract.query.all()}
    visit = Visit.query.filter_by(id=task_id).first()
    if not visit:
        return None
    return _serialize_task(visit, contracts, include_report=True)


def list_technician_cards():
    visits = Visit.query.all()
    tasks_per_technician = {}
    for visit in visits:
        if visit.technician_id:
            tasks_per_technician.setdefault(visit.technician_id, []).append(visit)

    cards = []
    for technician in Technician.query.order_by(Technician.name.asc()).all():
        assigned_visits = tasks_per_technician.get(technician.id, [])
        cards.append(
            {
                "id": technician.id,
                "name": technician.name,
                "initials": _initials(technician.name),
                "zone": technician.zone,
                "tasks_today": len(assigned_visits),
                "active": True,
                "active_label": "Activo",
                "active_badge": "success",
                "expertise": technician.expertise,
                "expert": technician.expert,
            }
        )
    return cards


def get_technician_card(technician_id):
    technician = Technician.query.filter_by(id=technician_id).first()
    if not technician:
        return None

    contracts = {contract.charger_id: contract for contract in Contract.query.all()}
    assigned_visits = sorted(
        technician.visits,
        key=lambda visit: (visit.planned_date or datetime.min, visit.id),
    )
    completed_visits = [visit for visit in assigned_visits if visit.status == "completada"]

    return {
        "id": technician.id,
        "name": technician.name,
        "initials": _initials(technician.name),
        "zone": technician.zone,
        "expertise": technician.expertise,
        "expert": technician.expert,
        "role": "Tecnico de campo",
        "email": _email_from_name(technician.name),
        "phone": _phone_from_id(technician.id),
        "specialization": "Incidencias criticas" if technician.expert else "Mantenimiento preventivo",
        "assigned_tasks": [_serialize_task(visit, contracts) for visit in assigned_visits],
        "stats": {
            "monthly_tasks": len(assigned_visits),
            "sla_compliance": _percentage(len(completed_visits), len(assigned_visits)),
            "avg_expertise": technician.expertise,
        },
    }


def list_risk_cards():
    contracts = {contract.charger_id: contract for contract in Contract.query.all()}
    now = datetime.now(UTC).replace(tzinfo=None)
    risks = []

    for visit in Visit.query.order_by(Visit.planned_date.asc(), Visit.id.asc()).all():
        if visit.status == "completada" or not visit.incidence:
            continue

        incidence = visit.incidence
        response_sla = RISK_RESPONSE_SLA_HOURS.get(incidence.priority, 8)
        elapsed_hours = 0.0
        if incidence.created_at:
            elapsed_hours = max((now - incidence.created_at).total_seconds() / 3600, 0)

        remaining_hours = response_sla - elapsed_hours
        severity = "critical" if remaining_hours <= 1 else "warning"
        risks.append(_serialize_risk(visit, contracts, elapsed_hours, remaining_hours, severity))

    risks.sort(key=lambda risk: (risk["severity_weight"], risk["remaining_hours"], risk["task"]["id"]))
    return risks


def get_risk_card(task_id):
    for risk in list_risk_cards():
        if risk["task"]["id"] == task_id:
            return risk
    return None


def list_map_tasks(tipo_filter="todos", estado_filter="todos", tecnico_filter="todos"):
    contracts = {contract.charger_id: contract for contract in Contract.query.all()}
    tasks = []

    for visit in Visit.query.order_by(Visit.id.asc()).all():
        task = _serialize_task(visit, contracts)
        map_task = {
            "id": task["id"],
            "tipo": task["type_key"],
            "lat": task["latitude"],
            "lng": task["longitude"],
            "direccion": task["address"],
            "estado": task["map_status_key"],
            "tecnico": task["technician_name"],
            "cliente": task["client"],
        }

        if map_task["lat"] is None or map_task["lng"] is None:
            continue
        tasks.append(map_task)

    if tipo_filter != "todos":
        tasks = [task for task in tasks if task["tipo"] == tipo_filter]

    if estado_filter != "todos":
        tasks = [task for task in tasks if task["estado"] == estado_filter]

    if tecnico_filter != "todos":
        tasks = [task for task in tasks if task["tecnico"] == tecnico_filter]

    technicians = [technician.name for technician in Technician.query.order_by(Technician.name.asc()).all()]
    return {"tareas": tasks, "tecnicos": technicians}


def list_zone_loads():
    technicians = list_technician_cards()
    total = max(len(technicians), 1)
    grouped = {}

    for technician in technicians:
        zone = technician["zone"]
        grouped.setdefault(zone, {"zone": zone, "count": 0})
        grouped[zone]["count"] += 1

    zone_rows = []
    for zone in sorted(grouped):
        count = grouped[zone]["count"]
        zone_rows.append(
            {
                "zone": zone,
                "count": count,
                "width": max(int((count / total) * 100), 10),
            }
        )
    return zone_rows


def _ensure_default_user():
    admin = User.query.filter(
        (User.email == "admin@smartmobility.com") | (User.username == "admin")
    ).first()

    if admin:
        admin.email = "admin@smartmobility.com"
        admin.username = "admin"
        admin.password = bcrypt.generate_password_hash("admin123").decode("utf-8")
        admin.nombre = "Admin"
        admin.apellido = "SmartMobility"
        admin.role = "admin"
        admin.zona = "Operaciones"
        admin.activo = True
    else:
        db.session.add(
            User(
                email="admin@smartmobility.com",
                username="admin",
                password=bcrypt.generate_password_hash("admin123").decode("utf-8"),
                nombre="Admin",
                apellido="SmartMobility",
                role="admin",
                zona="Operaciones",
                activo=True,
            )
        )

    db.session.commit()


def _serialize_task(visit, contracts, include_report=False):
    incidence = visit.incidence
    contract = contracts.get(incidence.charger_id) if incidence else None
    report = None
    if include_report and visit.reports:
        report = sorted(visit.reports, key=lambda item: item.created_at or datetime.min)[-1]

    zone = visit.technician.zone if visit.technician else _zone_from_address(visit.address)
    type_key = TYPE_KEYS.get(visit.visit_type, visit.visit_type)
    map_status_key = _map_status(visit)

    return {
        "id": visit.id,
        "type_label": TYPE_LABELS.get(visit.visit_type, visit.visit_type.title()),
        "type_key": type_key,
        "client": contract.client_id if contract else "Sin cliente",
        "charger_id": incidence.charger_id if incidence else "-",
        "address": visit.address,
        "zone": zone,
        "priority_key": incidence.priority if incidence else "baixa",
        "priority_label": PRIORITY_LABELS.get(incidence.priority, "Baja") if incidence else "Baja",
        "priority_badge": PRIORITY_BADGES.get(incidence.priority, "secondary") if incidence else "secondary",
        "status_key": visit.status,
        "status_label": VISIT_STATUS_LABELS.get(visit.status, visit.status.title()),
        "status_badge": VISIT_STATUS_BADGES.get(visit.status, "secondary"),
        "map_status_key": map_status_key,
        "map_status_label": MAP_STATUS_LABELS.get(map_status_key, "Pendiente"),
        "map_status_badge": MAP_STATUS_BADGES.get(map_status_key, "secondary"),
        "technician_id": visit.technician.id if visit.technician else None,
        "technician_name": visit.technician.name if visit.technician else None,
        "planned_date": visit.planned_date,
        "planned_date_label": _format_datetime(visit.planned_date),
        "description": incidence.description if incidence else "",
        "incidence_status_label": INCIDENCE_STATUS_LABELS.get(incidence.status, incidence.status.title()) if incidence else "-",
        "incidence_status_badge": INCIDENCE_STATUS_BADGES.get(incidence.status, "secondary") if incidence else "secondary",
        "visit_type_label": TYPE_LABELS.get(visit.visit_type, visit.visit_type.title()),
        "contract_type": contract.contract_type if contract else "-",
        "contract_status": contract.status if contract else "-",
        "latitude": visit.latitude if visit.latitude is not None else (contract.latitude if contract else None),
        "longitude": visit.longitude if visit.longitude is not None else (contract.longitude if contract else None),
        "report": _serialize_report(report) if report else None,
    }


def _serialize_report(report):
    return {
        "id": report.id,
        "type": report.report_type,
        "status": REPORT_STATUS_LABELS.get(report.status, report.status.title()),
        "status_badge": REPORT_STATUS_BADGES.get(report.status, "secondary"),
        "observations": report.observations,
        "created_at": _format_datetime(report.created_at),
    }


def _serialize_risk(visit, contracts, elapsed_hours, remaining_hours, severity):
    task = _serialize_task(visit, contracts)
    severity_label = "CRITICO" if severity == "critical" else "ADVERTENCIA"
    severity_badge = "danger" if severity == "critical" else "warning"
    severity_weight = 0 if severity == "critical" else 1

    return {
        "task": task,
        "severity": severity,
        "severity_label": severity_label,
        "severity_badge": severity_badge,
        "severity_weight": severity_weight,
        "remaining_hours": remaining_hours,
        "elapsed_label": _format_duration_hours(elapsed_hours),
        "response_sla_label": f"{RISK_RESPONSE_SLA_HOURS.get(visit.incidence.priority, 8)}h",
        "remaining_label": _remaining_label(remaining_hours),
    }


def _parse_location(location):
    if not location:
        return None, None
    return location.get("_latitude"), location.get("_longitude")


def _parse_timestamp(timestamp_data):
    if not timestamp_data:
        return None
    seconds = timestamp_data.get("_seconds", 0)
    if not seconds:
        return None
    return datetime.fromtimestamp(seconds, tz=UTC).replace(tzinfo=None)


def _map_status(visit):
    if visit.status == "completada":
        return "resuelta"
    if visit.technician_id:
        return "asignada"
    return "por_asignar"


def _zone_from_address(address):
    if not address:
        return "Sin zona"
    segments = [segment.strip() for segment in address.split(",") if segment.strip()]
    return segments[-1] if segments else address


def _format_datetime(value):
    if not value:
        return "-"
    return value.strftime("%d/%m/%Y %H:%M")


def _format_duration_hours(value):
    hours = max(value, 0)
    if hours < 1:
        return f"{int(hours * 60)} min"
    if abs(hours - round(hours)) < 0.05:
        return f"{int(round(hours))} h"
    return f"{hours:.1f} h"


def _remaining_label(remaining_hours):
    if remaining_hours <= 0:
        return f"SLA vencido hace {_format_duration_hours(abs(remaining_hours))}"
    return f"Quedan {_format_duration_hours(remaining_hours)}"


def _percentage(completed, total):
    if total == 0:
        return "0%"
    return f"{round((completed / total) * 100)}%"


def _initials(name):
    parts = [part for part in name.split() if part]
    if len(parts) == 1:
        return parts[0][:2].upper()
    return "".join(part[0] for part in parts[:2]).upper()


def _email_from_name(name):
    normalized = ".".join(name.lower().split())
    return f"{normalized}@smartmobility.com"


def _phone_from_id(technician_id):
    digits = "".join(character for character in technician_id if character.isdigit())
    suffix = digits.zfill(3)
    return f"600 12{suffix[:1]} {suffix[1:]}"
