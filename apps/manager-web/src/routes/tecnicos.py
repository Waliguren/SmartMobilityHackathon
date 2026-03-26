from flask import Blueprint, abort, render_template
from flask_login import login_required
from src.data_store import get_technician_card, list_technician_cards

tecnicos = Blueprint('tecnicos', __name__)

@tecnicos.route('/tecnicos')
@login_required
def lista_tecnicos():
    technicians = list_technician_cards()
    return render_template('tecnicos/lista.html', title='Técnicos', technicians=technicians)

@tecnicos.route('/tecnicos/<string:tecnico_id>')
@login_required
def detalle_tecnico(tecnico_id):
    technician = get_technician_card(tecnico_id)
    if not technician:
        abort(404)
    return render_template('tecnicos/detalle.html', title='Detalle Técnico', technician=technician)
