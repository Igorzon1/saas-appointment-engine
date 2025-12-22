from flask import Flask
from flask_jwt_extended import JWTManager 
from .db import init_db
from .config import SECRET_KEY, SQLALCHEMY_DATABASE_URI

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
        JWT_SECRET_KEY=SECRET_KEY  # <--- 2. CONFIG NOVA (Usamos a mesma chave para facilitar)
    )
    
    init_db(app)
    
    jwt = JWTManager(app) # <--- 3. INICIALIZAÇÃO NOVA
    
    app.register_blueprint(appointments_bp, url_prefix="/appointments")
    app.register_blueprint(dashboard_bp, url_prefix="/")
    app.register_blueprint(patients_bp, url_prefix="/patients")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    

    @app.route("/health")
    def health():
        return {"status": "ok"}
        
    return app