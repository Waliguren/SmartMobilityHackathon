from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

tecnicos = Blueprint('tecnicos', __name__)

@tecnicos.route('/tecnicos')
@login_required
def lista_tecnicos():
    return render_template('tecnicos/lista.html', title='Técnicos')

@tecnicos.route('/tecnicos/<int:tecnico_id>')
@login_required
def detalle_tecnico(tecnico_id):
    return render_template('tecnicos/detalle.html', title='Detalle Técnico', tecnico_id=tecnico_id)