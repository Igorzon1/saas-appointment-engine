from app.db import db
from datetime import datetime

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    service_type = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(20), default="scheduled")
    start_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    professional_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "service": self.service_type,
            "date": self.start_at.isoformat(),
            "status": self.status,
            "professional": self.professional_user.name if self.professional_user else None,
            "patient": self.patient_user.name if self.patient_user else None
        }
