import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

@login_manager.user_loader
def load_user(user_id):
    from src.models.user import User
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    os.makedirs(app.instance_path, exist_ok=True)
    
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    from src.routes.main import main
    from src.routes.tareas import tareas
    from src.routes.auth import auth
    from src.routes.tecnicos import tecnicos
    from src.routes.riesgos import riesgos
    from src.routes.mapa import mapa
    from src.routes.asignacion import asignacion

    
    app.register_blueprint(main)
    app.register_blueprint(tareas)
    app.register_blueprint(auth)
    app.register_blueprint(tecnicos)
    app.register_blueprint(riesgos)
    app.register_blueprint(mapa)
    app.register_blueprint(asignacion)
    
    from src.services.firebase_service import init_firebase
    init_firebase()
    
    with app.app_context():
        db.create_all()
        ensure_operational_data(app)
    
    return app
