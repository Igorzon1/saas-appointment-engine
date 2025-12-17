from .db import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='patient') # 'patient' ou 'professional'
    
    # Campo opcional para CPF (herdado da sua ideia antiga)
    cpf = db.Column(db.String(14))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # RELACIONAMENTOS (A "fiação" do banco)
    # Agendamentos onde este usuário é o PROFISSIONAL
    appointments_as_pro = db.relationship('Appointment', 
                                          foreign_keys='Appointment.professional_id', 
                                          backref='professional_user', 
                                          lazy=True)
    
    # Agendamentos onde este usuário é o PACIENTE
    appointments_as_patient = db.relationship('Appointment', 
                                              foreign_keys='Appointment.patient_id', 
                                              backref='patient_user', 
                                              lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role
        }

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    service_type = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(20), default="scheduled")
    start_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # CHAVES ESTRANGEIRAS (Aqui resolvemos o problema de ligar a pessoa certa)
    professional_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Nullable pois pode ser agendamento rápido

    def to_dict(self):
        return {
            "id": self.id,
            "service": self.service_type,
            "date": self.start_at.isoformat(),
            "status": self.status,
            "professional": self.professional_user.name if self.professional_user else None,
            "patient": self.patient_user.name if self.patient_user else None
        }