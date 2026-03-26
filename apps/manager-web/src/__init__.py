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
    
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'
    
    from src.routes.main import main
    from src.routes.tareas import tareas
    from src.routes.auth import auth
    from src.routes.tecnicos import tecnicos
    from src.routes.riesgos import riesgos
    
    app.register_blueprint(main)
    app.register_blueprint(tareas)
    app.register_blueprint(auth)
    app.register_blueprint(tecnicos)
    app.register_blueprint(riesgos)
    
    with app.app_context():
        db.create_all()
    
    return app