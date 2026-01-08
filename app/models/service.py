from app.db import db

class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) # Ex: Limpeza, Consulta, Canal
    duration_minutes = db.Column(db.Integer, nullable=False) # Ex: 30, 60, 45
    price = db.Column(db.Float, nullable=True)
    
    # Vincula o serviço a um profissional específico (opcional, se cada um tiver seus preços)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'))