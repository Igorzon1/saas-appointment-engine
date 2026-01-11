from datetime import datetime, timedelta, date, time
from flask import Blueprint, request, jsonify, render_template, session
from sqlalchemy import and_

# Imports do App
from app.db import db
from app.services.decorators import login_required
from app.services.appointment_service import AppointmentService
from app.models.appointment_models import Appointment
from app.models.professional import Professional, WorkingSchedule
from app.models.user_models import User

appointment_bp = Blueprint('appointments', __name__, url_prefix='/appointments')

@appointment_bp.route('/', methods=['POST'])
@login_required 
def create():
    """
    Cria um agendamento validando conflitos e horários.
    Recebe JSON: { date: 'YYYY-MM-DD HH:MM', service_text: '...', ... }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    try:
        # Chama o Service para validar e salvar
        new_appt = AppointmentService.create_appointment(
            professional_user_id=data.get('professional_id'),
            service_text=data.get('service_text'),
            start_str=data.get('date'),
            patient_user_id=data.get('patient_id'),
            guest_name=data.get('guest_name'),
            guest_phone=data.get('guest_phone')
        )
        
        return jsonify({
            "message": "Agendamento realizado com sucesso!",
            "id": new_appt.id,
            "time": f"{new_appt.start_at.strftime('%d/%m %H:%M')}"
        }), 201

    except ValueError as e:
        # Erros de validação (negócio) retornam 400
        return jsonify({"error": str(e)}), 400
        
    except Exception as e:
        # Erros inesperados retornam 500
        print(f"Erro CRÍTICO no agendamento: {e}")
        return jsonify({"error": "Erro interno ao processar agendamento."}), 500


@appointment_bp.route('/list', methods=['GET'])
@login_required
def list_view():
    """
    Renderiza a tela de agenda.
    """
    current_user_id = session['user']['id']
    
    # 1. Busca Profissional Logado (Para preencher o campo fixo e usar na busca)
    current_pro = Professional.query.filter_by(user_id=current_user_id).first()
    
    # 2. Busca Agendamentos (Ordenados por data, mais recentes primeiro)
    appointments = []
    if current_pro:
        appointments = Appointment.query.filter_by(professional_id=current_pro.id)\
            .order_by(Appointment.start_at.desc()).all()
    
    # 3. Busca Pacientes (Apenas os vinculados a este dentista)
    patients = User.query.filter_by(role='patient', dentist_id=current_user_id).all()

    return render_template(
        'appointments.html', 
        appointments=appointments, 
        patients=patients,
        current_pro=current_pro
    )


@appointment_bp.route('/available_slots', methods=['GET'])
@login_required
def get_available_slots():
    """
    API AJAX: Retorna horários livres para uma data específica.
    Uso: /appointments/available_slots?date=2024-10-10&professional_id=1
    """
    date_str = request.args.get('date')          # Formato YYYY-MM-DD
    pro_user_id = request.args.get('professional_id')

    if not date_str or not pro_user_id:
        return jsonify({"slots": [], "error": "Parâmetros incompletos"}), 400

    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # 1. Identificar o Profissional
        pro = Professional.query.filter_by(user_id=pro_user_id).first()
        if not pro:
            return jsonify({"slots": [], "error": "Profissional não encontrado"}), 404

        # 2. Descobrir dia da semana (Lógica: Python 0=Seg ... DB 1=Seg)
        # No Python: 0=Mon, 1=Tue, ..., 6=Sun
        # No nosso DB: 0=Sun, 1=Mon, ..., 6=Sat (conforme lógica do Service anterior)
        python_weekday = target_date.weekday() 
        db_weekday = (python_weekday + 1) % 7 

        # 3. Buscar Horário de Trabalho
        schedule = WorkingSchedule.query.filter_by(
            professional_id=pro.id, 
            day_of_week=db_weekday
        ).first()

        if not schedule:
            return jsonify({"slots": [], "message": "Não há atendimento neste dia."})

        # 4. Calcular Slots
        available_slots = []
        slot_duration = 60 # Minutos
        
        # Define horário de inicio e fim do dia
        current_time = datetime.combine(target_date, schedule.start_time)
        end_time_limit = datetime.combine(target_date, schedule.end_time)

        # 5. Buscar agendamentos JÁ OCUPADOS neste dia
        busy_appointments = Appointment.query.filter(
            Appointment.professional_id == pro.id,
            Appointment.status != 'cancelled',
            Appointment.start_at >= datetime.combine(target_date, time.min),
            Appointment.start_at <= datetime.combine(target_date, time.max)
        ).all()

        # Loop para gerar horários (08:00, 09:00, etc)
        while current_time + timedelta(minutes=slot_duration) <= end_time_limit:
            
            slot_start = current_time
            slot_end = current_time + timedelta(minutes=slot_duration)
            
            # Verifica colisão
            is_busy = False
            for appt in busy_appointments:
                # Se o slot começa antes do agendamento terminar E termina depois do agendamento começar
                if slot_start < appt.end_at and slot_end > appt.start_at:
                    is_busy = True
                    break
            
            if not is_busy:
                # Adiciona na lista apenas a hora (HH:MM)
                available_slots.append(slot_start.strftime("%H:%M"))

            # Avança para o próximo slot
            current_time += timedelta(minutes=slot_duration)

        return jsonify({"slots": available_slots})

    except Exception as e:
        print(f"Erro ao calcular slots: {e}")
        return jsonify({"slots": [], "error": "Erro interno ao calcular horários"}), 500