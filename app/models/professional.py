from app.db import db

class Professional(db.Model):
    __tablename__ = 'professionals'

    id = db.Column(db.Integer, primary_key=True)
    # Chave estrangeira 1-para-1 com User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    crm = db.Column(db.String(20))
    color = db.Column(db.String(10)) # Para o calendário no front
    
    # Relacionamentos
    #services = db.relationship('Service', backref='professional', lazy=True)
    schedules = db.relationship('WorkingSchedule', backref='professional', lazy=True)

class WorkingSchedule(db.Model):
    """Define a disponibilidade padrão (Ex: Toda Seg das 08:00 as 12:00)"""
    __tablename__ = 'working_schedules'

    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), nullable=False)
    
    day_of_week = db.Column(db.Integer, nullable=False) # 0=Dom, 1=Seg... 6=Sab
    start_time = db.Column(db.Time, nullable=False) # Ex: 08:00
    end_time = db.Column(db.Time, nullable=False)   # Ex: 12:00