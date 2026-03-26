from flask import Blueprint, render_template
from flask_login import login_required

riesgos = Blueprint('riesgos', __name__)

@riesgos.route('/riesgos')
@login_required
def lista_riesgos():
    return render_template('riesgos/lista.html', title='Riesgos SLA')

@riesgos.route('/riesgos/<int:riesgo_id>')
@login_required
def detalle_riesgo(riesgo_id):
    return render_template('riesgos/detalle.html', title='Detalle Riesgo', riesgo_id=riesgo_id)