from flask import Blueprint, abort, render_template, request
from flask_login import login_required
from src.data_store import get_task_card, list_task_cards, list_technician_cards

tareas = Blueprint('tareas', __name__)

@tareas.route('/tareas')
@login_required
def lista_tareas():
    tipo = request.args.get('tipo', '')
    zona = request.args.get('zona', '')
    prioridad = request.args.get('prioridad', '')
    query = request.args.get('q', '').strip().lower()

    tasks = list_task_cards()

    if tipo:
        tasks = [task for task in tasks if task['type_key'] == tipo]
    if zona:
        tasks = [task for task in tasks if task['zone'].lower() == zona.lower()]
    if prioridad:
        tasks = [task for task in tasks if task['priority_key'] == prioridad]
    if query:
        tasks = [
            task for task in tasks
            if query in task['id'].lower()
            or query in task['client'].lower()
            or query in task['address'].lower()
            or (task['technician_name'] and query in task['technician_name'].lower())
        ]

    zones = sorted({task['zone'] for task in list_task_cards()})
    return render_template(
        'tareas/lista.html',
        title='Gestión de Tareas',
        tasks=tasks,
        zones=zones,
        filters={"tipo": tipo, "zona": zona, "prioridad": prioridad, "q": request.args.get('q', '')},
    )

@tareas.route('/tareas/<string:tarea_id>')
@login_required
def detalle_tarea(tarea_id):
    task = get_task_card(tarea_id)
    if not task:
        abort(404)

    technicians = list_technician_cards()
    recommended_technician = None
    for technician in technicians:
        if technician['zone'] == task['zone']:
            recommended_technician = technician
            break
    if not recommended_technician and technicians:
        recommended_technician = technicians[0]

    priority_score = {
        'alta': 92,
        'mitja': 73,
        'baixa': 48,
    }.get(task['priority_key'], 50)

    return render_template(
        'tareas/detalle.html',
        title='Detalle Tarea',
        task=task,
        technicians=technicians,
        recommended_technician=recommended_technician,
        priority_score=priority_score,
    )
