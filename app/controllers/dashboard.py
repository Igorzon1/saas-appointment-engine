from flask import Blueprint, render_template, session, redirect, url_for, flash
from flask_jwt_extended import jwt_required
from datetime import datetime, date, time
from app.models.appointment_models import Appointment
from app.models.user_models import User as Patient
from app.db import db
from ..services.decorators import login_required

bp = Blueprint("dashboard", __name__, template_folder="../views/templates")

@bp.route("/")
@login_required  # Protege - exige login
def index():
    # Definir o início e o fim do dia de hoje para filtrar
    hoje = date.today()
    inicio_dia = datetime.combine(hoje, time.min)
    fim_dia = datetime.combine(hoje, time.max)

    # Somente profissionais veem o dashboard
    me = session.get('user')
    if not me or me.get('role') != 'professional':
        flash('Acesso ao painel restrito a profissionais', 'danger')
        return redirect(url_for('auth.login_view'))

    # Buscar todos os agendamentos de HOJE para este profissional
    agendamentos_hoje = Appointment.query.filter(
        Appointment.professional_id == me['id'],
        Appointment.start_at >= inicio_dia,
        Appointment.start_at <= fim_dia
    ).order_by(Appointment.start_at.asc()).all()

    # Calcular contagens para os Cards
    count_total = len(agendamentos_hoje)
    
    # Contar quantos estão "scheduled" (Na fila)
    count_waiting = sum(1 for a in agendamentos_hoje if a.status == 'scheduled')
    
    # Contar quantos estão "in_service" (Em atendimento)
    count_in_service = sum(1 for a in agendamentos_hoje if a.status == 'in_service')

    return render_template(
        "dashboard.html",
        agendamentos=agendamentos_hoje,
        count_total=count_total,
        count_waiting=count_waiting,
        count_in_service=count_in_service,
        recent_patients=Patient.query.filter_by(dentist_id=me['id']).order_by(Patient.created_at.desc()).limit(5).all()
    )
