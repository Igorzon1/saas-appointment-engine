from flask import Blueprint, render_template, session, redirect, url_for, flash
from datetime import datetime, date, time
from app.models.appointment_models import Appointment
from app.models.user_models import User as Patient
from app.models.professional import Professional # <--- IMPORTANTE: Importar o model Professional
from app.db import db
from ..services.decorators import login_required

bp = Blueprint("dashboard", __name__, template_folder="../views/templates")

@bp.route("/")
@login_required 
def index():
    # 1. Obter usuário da sessão
    me = session.get('user')
    
    # 2. CORREÇÃO DO LOOP: Aceitar 'dentist' e 'clinic' também
    roles_permitidos = ['professional', 'dentist', 'clinic']
    
    if not me or me.get('role') not in roles_permitidos:
        flash('Acesso ao painel restrito a profissionais.', 'danger')
        return redirect(url_for('auth.login_view'))

    # 3. CORREÇÃO DE DADOS: Buscar o ID do Profissional
    # A tabela Appointment usa o ID da tabela 'professionals', não da tabela 'users'
    current_pro = Professional.query.filter_by(user_id=me['id']).first()
    
    if not current_pro:
        flash('Perfil profissional não encontrado. Entre em contato com suporte.', 'warning')
        # Opcional: Redirecionar ou mostrar dashboard vazio
        return render_template("dashboard.html", agendamentos=[], count_total=0, count_waiting=0, count_in_service=0, recent_patients=[])

    # Definir o início e o fim do dia de hoje
    hoje = date.today()
    inicio_dia = datetime.combine(hoje, time.min)
    fim_dia = datetime.combine(hoje, time.max)

    # 4. Buscar agendamentos usando o ID DO PROFISSIONAL (current_pro.id)
    agendamentos_hoje = Appointment.query.filter(
        Appointment.professional_id == current_pro.id, # <--- Mudança aqui
        Appointment.start_at >= inicio_dia,
        Appointment.start_at <= fim_dia
    ).order_by(Appointment.start_at.asc()).all()

    # Calcular contagens
    count_total = len(agendamentos_hoje)
    count_waiting = sum(1 for a in agendamentos_hoje if a.status == 'scheduled')
    count_in_service = sum(1 for a in agendamentos_hoje if a.status == 'in_service')

    # Buscar pacientes recentes (Aqui mantemos me['id'] se o dentist_id no User for o ID de Usuário)
    recent_patients = Patient.query.filter_by(dentist_id=me['id']).order_by(Patient.created_at.desc()).limit(5).all()

    return render_template(
        "dashboard.html",
        agendamentos=agendamentos_hoje,
        count_total=count_total,
        count_waiting=count_waiting,
        count_in_service=count_in_service,
        recent_patients=recent_patients,
        current_pro=current_pro # Envia o perfil profissional para o template se precisar
    )