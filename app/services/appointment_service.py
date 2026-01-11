from datetime import datetime, timedelta
from sqlalchemy import and_
from app.db import db
from app.models.appointment_models import Appointment
from app.models.professional import Professional, WorkingSchedule # <--- Importar Schedule

class AppointmentService:
    @staticmethod
    def create_appointment(professional_user_id, service_text, start_str, patient_user_id=None, guest_name=None, guest_phone=None):
        
        # ... (Validações de input iguais ao anterior) ...
        if not service_text:
            raise ValueError("Descrição do serviço obrigatória.")
        if not patient_user_id and not guest_name:
            raise ValueError("Informe o paciente.")

        # Conversão da data (formato esperado: YYYY-MM-DD HH:MM)
        try:
            clean_date_str = start_str.replace('T', ' ')
            start_at = datetime.strptime(clean_date_str, '%Y-%m-%d %H:%M')
        except ValueError:
            raise ValueError("Data inválida.")

        # Busca Profissional
        professional = Professional.query.filter_by(user_id=professional_user_id).first()
        if not professional:
            raise ValueError("Profissional não encontrado.")

        # --- NOVA VALIDAÇÃO: HORÁRIO DE TRABALHO ---
        # 1. Descobrir qual dia da semana é (Python: 0=Seg, 6=Dom | Nosso Banco: 0=Dom, 1=Seg...)
        # Vamos converter Python weekday para o nosso padrão (0=Dom)
        python_weekday = start_at.weekday() # 0=Mon, ... 6=Sun
        db_weekday = (python_weekday + 1) % 7 # Converte para 0=Dom, 1=Seg, etc.

        # 2. Buscar se o profissional atende nesse dia
        work_schedule = WorkingSchedule.query.filter_by(
            professional_id=professional.id, 
            day_of_week=db_weekday
        ).first()

        if not work_schedule:
            raise ValueError(f"O profissional não atende neste dia da semana.")

        # 3. Verificar se o horário está dentro do expediente
        # Extrai apenas a HORA do agendamento solicitado
        req_time = start_at.time()
        
        # Cálculo do fim do atendimento (Duração Padrão 60min)
        duration_minutes = 60 
        end_at = start_at + timedelta(minutes=duration_minutes)
        req_end_time = end_at.time()

        # Verifica limites (Início >= InícioExpediente E Fim <= FimExpediente)
        if req_time < work_schedule.start_time or req_end_time > work_schedule.end_time:
             raise ValueError(f"Horário fora do expediente ({work_schedule.start_time.strftime('%H:%M')} às {work_schedule.end_time.strftime('%H:%M')}).")

        # --- FIM DA NOVA VALIDAÇÃO ---

        # 4. Verificação de Conflito (Choque com outros agendamentos)
        conflict = Appointment.query.filter(
            Appointment.professional_id == professional.id,
            Appointment.status != 'cancelled',
            and_(
                Appointment.start_at < end_at,
                Appointment.end_at > start_at
            )
        ).first()

        if conflict:
            raise ValueError(f"Horário indisponível! Já existe agendamento às {conflict.start_at.strftime('%H:%M')}.")

        # 5. Salva
        new_appointment = Appointment(
            professional_id=professional.id,
            service_description=service_text,
            start_at=start_at,
            end_at=end_at,
            status='scheduled',
            patient_id=patient_user_id if patient_user_id else None,
            guest_name=guest_name if not patient_user_id else None,
            guest_phone=guest_phone if not patient_user_id else None
        )

        db.session.add(new_appointment)
        db.session.commit()

        return new_appointment