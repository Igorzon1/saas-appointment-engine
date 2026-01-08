from app.db import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='patient')
    cpf = db.Column(db.String(14))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- RELAÇÃO COM DENTISTA (Pode manter) ---
    dentist_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    patients = db.relationship('User',
                               backref=db.backref('dentist', remote_side=[id]),
                               lazy='dynamic')

    # --- PERFIL PROFISSIONAL (Pode manter) ---
    professional_profile = db.relationship('Professional', backref='user', uselist=False)

    # ------------------------------------------------------------------
    # ❌ REMOVA O BLOCO 'appointments_as_patient' DAQUI
    # ------------------------------------------------------------------
    # A relação já está sendo criada no arquivo appointment_models.py
    # através do backref lá. Se você deixar aqui, dá o erro de duplicação.

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