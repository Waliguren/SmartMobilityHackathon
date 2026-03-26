from flask import Blueprint, render_template, request
from flask_login import login_required

mapa = Blueprint('mapa', __name__)

@mapa.route('/mapa')
@login_required
def vista_mapa():
    return render_template('mapa.html', title='Mapa de Tareas')

@mapa.route('/api/tareas-mapa')
@login_required
def tareas_mapa():
    tareas = [
        {"id": 1, "tipo": "incidencia", "lat": 41.3874, "lng": 2.1686, "direccion": "C/ Major, 23 - Barcelona", "estado": "por_asignar", "tecnico": None, "cliente": "ElektroPlus"},
        {"id": 2, "tipo": "mantenimiento", "lat": 40.4168, "lng": -3.7038, "direccion": "Av. Gran Vía, 45 - Madrid", "estado": "asignada", "tecnico": "Juan García", "cliente": "CityParking"},
        {"id": 3, "tipo": "puesta_marcha", "lat": 39.4699, "lng": -0.3763, "direccion": "C/ de Colón, 12 - Valencia", "estado": "asignada", "tecnico": "María López", "cliente": "Hotel Mar"},
        {"id": 4, "tipo": "incidencia", "lat": 37.3833, "lng": -5.9967, "direccion": "Av. de la Constitución, 78 - Sevilla", "estado": "por_asignar", "tecnico": None, "cliente": "Aparcamientos Sur"},
        {"id": 5, "tipo": "mantenimiento", "lat": 43.2627, "lng": -2.9450, "direccion": "Gran Vía, 25 - Bilbao", "estado": "resuelta", "tecnico": "Pedro Sánchez", "cliente": "Parking Bilbao"},
        {"id": 6, "tipo": "incidencia", "lat": 36.7213, "lng": -4.4214, "direccion": "C/ Larios, 34 - Málaga", "estado": "asignada", "tecnico": "Juan García", "cliente": "Parking Centro"},
        {"id": 7, "tipo": "puesta_marcha", "lat": 42.8125, "lng": -1.6458, "direccion": "Av. Pío XII, 56 - Pamplona", "estado": "por_asignar", "tecnico": None, "cliente": "Hotel Laperla"},
        {"id": 8, "tipo": "mantenimiento", "lat": 41.6488, "lng": -0.8891, "direccion": "C/ Alfonso I, 22 - Zaragoza", "estado": "asignada", "tecnico": "María López", "cliente": "Aparcamientos Zaragoza"},
        {"id": 9, "tipo": "incidencia", "lat": 28.2916, "lng": -16.6291, "direccion": "Av. de la Constitución, 1 - Santa Cruz Tenerife", "estado": "resuelta", "tecnico": "Pedro Sánchez", "cliente": "Parking Tenerife"},
        {"id": 10, "tipo": "puesta_marcha", "lat": 35.0, "lng": -9.5, "direccion": "Las Palmas de Gran Canaria", "estado": "por_asignar", "tecnico": None, "cliente": "Hotel Paradise"},
    ]
    
    tipo_filter = request.args.get('tipo', 'todos')
    estado_filter = request.args.get('estado', 'todos')
    tecnico_filter = request.args.get('tecnico', 'todos')
    
    filtered_tareas = tareas
    
    if tipo_filter != 'todos':
        filtered_tareas = [t for t in filtered_tareas if t['tipo'] == tipo_filter]
    
    if estado_filter != 'todos':
        filtered_tareas = [t for t in filtered_tareas if t['estado'] == estado_filter]
    
    if tecnico_filter != 'todos':
        filtered_tareas = [t for t in filtered_tareas if t['tecnico'] == tecnico_filter]
    
    tecnicos = list(set([t['tecnico'] for t in tareas if t['tecnico']]))
    
    return {"tareas": filtered_tareas, "tecnicos": tecnicos}