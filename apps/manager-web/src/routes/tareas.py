
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from src.services.firebase_service import get_visits, get_incidents, get_contracts


tareas = Blueprint('tareas', __name__)

@tareas.route('/tareas')
@login_required
def lista_tareas():

    visits = get_visits()
    incidents = get_incidents()
    contracts = get_contracts()
    
    tasks = []
    for visit in visits:
        task = visit.copy()
        
        for inc in incidents:
            if inc.get('id') == visit.get('incidence_id'):
                task['incidence'] = inc
                break
        
        for contract in contracts:
            if contract.get('id') == inc.get('charger_id'):
                task['contract'] = contract
                break
        
        task['tipo_display'] = {
            'avaria': 'Incidencia',
            'manteniment': 'Mantenimiento',
            'preventiu': 'Preventivo'
        }.get(task.get('visit_type', ''), task.get('visit_type', ''))
        
        task['estado_display'] = {
            'pendent': 'Pendiente',
            'en_proces': 'En proceso',
            'completada': 'Completada'
        }.get(task.get('status', ''), task.get('status', ''))
        
        tasks.append(task)
    
    return render_template('tareas/lista.html', title='Gestión de Tareas', tasks=tasks)

@tareas.route('/tareas/<tarea_id>')
@login_required
def detalle_tarea(tarea_id):
    visits = get_visits()
    incidents = get_incidents()
    contracts = get_contracts()
    
    task = None
    for visit in visits:
        if visit.get('id') == tarea_id:
            task = visit.copy()
            break
    
    if task:
        for inc in incidents:
            if inc.get('id') == task.get('incidence_id'):
                task['incidence'] = inc
                break
        
        task['tipo_display'] = {
            'avaria': 'Incidencia',
            'manteniment': 'Mantenimiento',
            'preventiu': 'Preventivo'
        }.get(task.get('visit_type', ''), task.get('visit_type', ''))
        
        task['estado_display'] = {
            'pendent': 'Pendiente',
            'en_proces': 'En proceso',
            'completada': 'Completada'
        }.get(task.get('status', ''), task.get('status', ''))
    
    return render_template('tareas/detalle.html', title='Detalle Tarea', tarea_id=tarea_id, task=task)

