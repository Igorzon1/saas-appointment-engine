from app.db import db
from datetime import datetime

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    
    # --- MUDANÇA: Serviço agora é texto livre ---
    service_description = db.Column(db.String(150), nullable=False)
    
    # FKs
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), nullable=False, index=True)
    
    # Paciente é opcional (pode ser NULL se for um convidado)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Campos para Paciente Avulso (Convidado)
    guest_name = db.Column(db.String(100), nullable=True)
    guest_phone = db.Column(db.String(20), nullable=True)

    # Datas
    start_at = db.Column(db.DateTime, nullable=False, index=True)
    end_at = db.Column(db.DateTime, nullable=False, index=True)
    
    status = db.Column(db.String(20), default="scheduled")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    professional = db.relationship('Professional', backref='appointments')
    patient_user = db.relationship('User', foreign_keys=[patient_id], backref='my_appointments')

    def to_dict(self):
        return {
            "id": self.id,
            "service": self.service_description,
            "start": self.start_at.isoformat(),
            "end": self.end_at.isoformat(),
            "status": self.status,
            "patient_name": self.patient_user.name if self.patient_user else self.guest_name
        }