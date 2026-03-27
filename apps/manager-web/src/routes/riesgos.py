from flask import Blueprint, abort, render_template
from flask_login import login_required
from src.data_store import get_risk_card, list_risk_cards

riesgos = Blueprint('riesgos', __name__)

@riesgos.route('/riesgos')
@login_required
def lista_riesgos():
    risks = list_risk_cards()
    return render_template('riesgos/lista.html', title='Riesgos SLA', risks=risks)

@riesgos.route('/riesgos/<string:riesgo_id>')
@login_required
def detalle_riesgo(riesgo_id):
    risk = get_risk_card(riesgo_id)
    if not risk:
        abort(404)
    return render_template('riesgos/detalle.html', title='Detalle Riesgo', risk=risk)
