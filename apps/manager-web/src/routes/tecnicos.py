from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from src.services.firebase_service import get_technicians, get_visits


tecnicos = Blueprint('tecnicos', __name__)

@tecnicos.route('/tecnicos')
@login_required
def lista_tecnicos():

    technicians = get_technicians()
    return render_template('tecnicos/lista.html', title='Técnicos', tecnicos=technicians)

@tecnicos.route('/tecnicos/<tecnico_id>')
@login_required
def detalle_tecnico(tecnico_id):
    technicians = get_technicians()
    visits = get_visits()
    
    tecnico = None
    for t in technicians:
        if t.get('id') == tecnico_id:
            tecnico = t
            break
    
    tareas_hoy = []
    for visit in visits:
        if visit.get('technician_id') == tecnico_id:
            tareas_hoy.append(visit)
    
    return render_template('tecnicos/detalle.html', title='Detalle Técnico', tecnico_id=tecnico_id, tecnico=tecnico, tareas=tareas_hoy)

