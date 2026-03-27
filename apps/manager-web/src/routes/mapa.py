from flask import Blueprint, render_template, request
from flask_login import login_required
from src.data_store import list_map_tasks, list_technician_cards

mapa = Blueprint('mapa', __name__)

@mapa.route('/mapa')
@login_required
def vista_mapa():
    technicians = list_technician_cards()
    return render_template('mapa.html', title='Mapa de Tareas', technicians=technicians)

@mapa.route('/api/tareas-mapa')
@login_required
def tareas_mapa():
    tipo_filter = request.args.get('tipo', 'todos')
    estado_filter = request.args.get('estado', 'todos')
    tecnico_filter = request.args.get('tecnico', 'todos')
    return list_map_tasks(tipo_filter, estado_filter, tecnico_filter)
