from app.db import db

class Professional(db.Model):
    __tablename__ = 'professionals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Aqui guardaremos o CRM (se for dentista) ou CNPJ (se for clínica)
    crm = db.Column(db.String(20)) 
    color = db.Column(db.String(10)) 
    
    schedules = db.relationship('WorkingSchedule', backref='professional', lazy=True)

    def to_dict(self):
        """Serializa os dados do profissional/clínica"""
        return {
            "id": self.id,
            "document": self.crm, # Retorna o CRM ou CNPJ
            "color": self.color
        }
    
class WorkingSchedule(db.Model):
    """Define a disponibilidade padrão (Ex: Toda Seg das 08:00 as 12:00)"""
    __tablename__ = 'working_schedules'

    id = db.Column(db.Integer, primary_key=True)
    
    # FK ligando ao Profissional
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), nullable=False)
    
    day_of_week = db.Column(db.Integer, nullable=False) # 0=Dom, 1=Seg... 6=Sab
    start_time = db.Column(db.Time, nullable=False) # Ex: 08:00
    end_time = db.Column(db.Time, nullable=False)   # Ex: 12:00

    def to_dict(self):
        return {
            "day_of_week": self.day_of_week,
            "start_time": self.start_time.strftime("%H:%M"),
            "end_time": self.end_time.strftime("%H:%M")
        }