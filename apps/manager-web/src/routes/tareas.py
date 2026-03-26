from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from src.models.user import User

tareas = Blueprint('tareas', __name__)

@tareas.route('/tareas')
@login_required
def lista_tareas():
    return render_template('tareas/lista.html', title='Gestión de Tareas')

@tareas.route('/tareas/<int:tarea_id>')
@login_required
def detalle_tarea(tarea_id):
    return render_template('tareas/detalle.html', title='Detalle Tarea', tarea_id=tarea_id)