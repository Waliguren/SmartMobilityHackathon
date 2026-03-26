from flask import Blueprint, render_template
from flask_login import login_required, current_user
from src.data_store import build_dashboard_context, list_zone_loads

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/dashboard')
@login_required
def dashboard():
    context = build_dashboard_context()
    return render_template('dashboard.html', title='Dashboard', **context)

@main.route('/panel')
@login_required
def panel():
    context = build_dashboard_context()
    zone_loads = list_zone_loads()
    return render_template('panel.html', title='Panel Principal', zone_loads=zone_loads, **context)
