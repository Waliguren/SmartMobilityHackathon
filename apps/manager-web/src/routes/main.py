from flask import Blueprint, render_template
from flask_login import login_required
from src.services.firebase_service import get_visits, get_technicians, get_incidents

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/dashboard')
@login_required
def dashboard():
    visits = get_visits()
    technicians = get_technicians()
    incidents = get_incidents()
    
    tareas_pendientes = sum(1 for v in visits if v.get('status') in ['pendent', 'en_proces'])
    tecnicos_activos = sum(1 for t in technicians if t.get('zone'))
    riesgos_sla = sum(1 for inc in incidents if inc.get('status') in ['oberta', 'en_proces'] and inc.get('priority') == 'alta')
    
    return render_template('dashboard.html', title='Dashboard', 
                         tareas_pendientes=tareas_pendientes,
                         tecnicos_activos=tecnicos_activos,
                         riesgos_sla=riesgos_sla)