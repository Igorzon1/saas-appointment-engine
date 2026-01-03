from flask import Flask
from flask_jwt_extended import JWTManager 
from .db import init_db, db
from .config import SECRET_KEY, SQLALCHEMY_DATABASE_URI
from flask_migrate import Migrate

from .controllers.appointments import appointment_bp as appointments_bp
from .controllers.auth import auth_bp as auth_bp
from .controllers.dashboard import bp as dashboard_bp
from .controllers.patients import bp as patients_bp 

def create_app():
    app = Flask(__name__, template_folder="views/templates")
    
    app.config.update(
        SECRET_KEY=SECRET_KEY,
        SQLALCHEMY_DATABASE_URI=SQLALCHEMY_DATABASE_URI,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY=SECRET_KEY,
        SESSION_PERMANENT=False,  # NOVO
        SESSION_TYPE='filesystem'  # NOVO
    )
    
    init_db(app)
    
    jwt = JWTManager(app)
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)
    
    app.register_blueprint(appointments_bp, url_prefix="/appointments")
    app.register_blueprint(dashboard_bp, url_prefix="/")
    app.register_blueprint(patients_bp, url_prefix="/patients")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    

    @app.route("/health")
    def health():
        return {"status": "ok"}
        
    return app