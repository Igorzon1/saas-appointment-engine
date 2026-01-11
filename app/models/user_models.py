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
    role = db.Column(db.String(20), default='patient') # Pode ser 'patient', 'dentist', 'clinic'
    cpf = db.Column(db.String(14))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    dentist_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    patients = db.relationship('User', backref=db.backref('dentist', remote_side=[id]), lazy='dynamic')
    
    # Cascade garante que se deletar o user, deleta o perfil profissional
    professional_profile = db.relationship('Professional', backref='user', uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        data = {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "phone": self.phone
        }
        # AQUI ESTÁ A MÁGICA: Se tiver perfil profissional, anexa os dados dele
        if self.professional_profile:
            data['professional'] = self.professional_profile.to_dict()
        
        return data