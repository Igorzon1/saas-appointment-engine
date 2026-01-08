from datetime import datetime, timedelta
from sqlalchemy import and_
from app.db import db
from app.models.appointment_models import Appointment
from app.models.professional import Professional

class AppointmentService:
    @staticmethod
    def create_appointment(professional_user_id, service_text, start_str, patient_user_id=None, guest_name=None, guest_phone=None):
        """
        Cria agendamento com serviço em texto livre.
        Duração padrão fixada em 60 minutos para cálculo de conflito.
        """

        # 1. Validações Iniciais
        if not service_text:
            raise ValueError("A descrição do serviço/procedimento é obrigatória.")

        if not patient_user_id and not guest_name:
            raise ValueError("Selecione um Paciente cadastrado ou digite o Nome do convidado.")

        # 2. Conversão de Data
        try:
            # Remove o 'T' que vem do input datetime-local do HTML
            clean_date_str = start_str.replace('T', ' ')
            start_at = datetime.strptime(clean_date_str, '%Y-%m-%d %H:%M')
        except ValueError:
            raise ValueError("Formato de data inválido.")

        # 3. Busca o Profissional (baseado no User ID logado)
        professional = Professional.query.filter_by(user_id=professional_user_id).first()
        if not professional:
            raise ValueError("Perfil profissional não encontrado para este usuário.")

        # 4. Cálculo de Horário (Padrão 1 Hora)
        # Como é texto livre, assumimos 1h. Se quiser mudar, altere o 60 abaixo.
        duration_minutes = 60 
        end_at = start_at + timedelta(minutes=duration_minutes)

        # 5. Verificação de Conflito (Anti-Crash)
        conflict = Appointment.query.filter(
            Appointment.professional_id == professional.id,
            Appointment.status != 'cancelled',
            and_(
                Appointment.start_at < end_at,
                Appointment.end_at > start_at
            )
        ).first()

        if conflict:
            raise ValueError(f"Conflito! Já existe agendamento às {conflict.start_at.strftime('%H:%M')}.")

        # 6. Salvar no Banco
        new_appointment = Appointment(
            professional_id=professional.id,
            service_description=service_text, # Salva o texto digitado
            start_at=start_at,
            end_at=end_at,
            status='scheduled',
            
            # Lógica: Usa ID se tiver, senão usa os dados de convidado
            patient_id=patient_user_id if patient_user_id else None,
            guest_name=guest_name if not patient_user_id else None,
            guest_phone=guest_phone if not patient_user_id else None
        )

        db.session.add(new_appointment)
        db.session.commit()

        return new_appointment