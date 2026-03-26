from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard')

@main.route('/panel')
@login_required
def panel():
    return render_template('panel.html', title='Panel Principal')