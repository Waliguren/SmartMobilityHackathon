from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from src import db
from src.models.user import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Hardcoded login for testing (no DB needed)
        if email == 'admin@smartmobility.com' and password == 'admin123':
            # Create a simple user object for Flask-Login
            user = User(
                id=1,
                email='admin@smartmobility.com',
                username='admin',
                password='admin123',
                nombre='Admin',
                apellido='User',
                role='admin'
            )
            login_user(user)
            flash('¡Bienvenido!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Email o contraseña incorrectos', 'danger')
    
    return render_template('auth/login.html', title='Iniciar Sesión')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        user = User(
            email=email,
            username=username,
            password=hashed_password,
            nombre=nombre,
            apellido=apellido,
            role='operador'
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Cuenta creada correctamente. Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
        except:
            flash('Error: El email o username ya existen', 'danger')
    
    return render_template('auth/register.html', title='Registrarse')