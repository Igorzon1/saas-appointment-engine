from flask import Blueprint, render_template, session, redirect, url_for, flash
from datetime import datetime, date, time
from app.models.appointment_models import Appointment
from app.models.user_models import User as Patient
from app.models.professional import Professional
from app.db import db
from ..services.decorators import login_required, role_required

bp = Blueprint("dashboard", __name__, template_folder="../views/templates")

@bp.route("/")
@login_required 
@role_required(['dentist', 'clinic', 'professional']) # Garante a permissão correta
def index():
    # 1. Obter usuário da sessão
    me = session.get('user')
    
    # 2. Buscar o Perfil Profissional
    # A tabela Appointment usa o ID da tabela 'professionals'
    current_pro = Professional.query.filter_by(user_id=me['id']).first()
    
    if not current_pro:
        flash('Perfil profissional não encontrado. Entre em contato com suporte.', 'warning')
        return render_template("dashboard.html", agendamentos=[], count_total=0, count_waiting=0, count_today=0, recent_patients=[])

    # 3. Definir data de referência (Hoje, 00:00:00)
    hoje = date.today()
    inicio_hoje = datetime.combine(hoje, time.min)

    # 4. Buscar Agendamentos (DO FUTURO E HOJE)
    # Filtra tudo que for maior ou igual a hoje (>=) e que não esteja cancelado
    agendamentos_futuros = Appointment.query.filter(
        Appointment.professional_id == current_pro.id,
        Appointment.start_at >= inicio_hoje, # <--- AQUI ESTAVA O PROBLEMA ANTES (era só hoje)
        Appointment.status != 'cancelled'
    ).order_by(Appointment.start_at.asc()).all()

    # 5. Calcular contagens
    count_total = len(agendamentos_futuros)
    
    # Conta quantos estão na fila (status = scheduled)
    count_waiting = sum(1 for a in agendamentos_futuros if a.status == 'scheduled')
    
    # Conta quantos são EXATAMENTE HOJE (para você ter noção da urgência)
    count_today = sum(1 for a in agendamentos_futuros if a.start_at.date() == hoje)
    
    # Conta quantos estão em atendimento
    count_in_service = sum(1 for a in agendamentos_futuros if a.status == 'in_service')

    # 6. Buscar pacientes recentes vinculados a este profissional
    recent_patients = Patient.query.filter_by(dentist_id=me['id']).order_by(Patient.created_at.desc()).limit(5).all()

    return render_template(
        "dashboard.html",
        agendamentos=agendamentos_futuros, # Manda a lista completa (hoje + futuro)
        count_total=count_total,
        count_waiting=count_waiting,
        count_today=count_today, # Nova variável para o template
        count_in_service=count_in_service,
        recent_patients=recent_patients,
        current_pro=current_pro
    )