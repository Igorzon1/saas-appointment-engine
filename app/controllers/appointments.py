from flask import Blueprint, request, jsonify, render_template, session
from app.services.decorators import login_required
from app.services.appointment_service import AppointmentService
from app.models.appointment_models import Appointment
from app.models.professional import Professional
from app.models.user_models import User

appointment_bp = Blueprint('appointments', __name__, url_prefix='/appointments')

@appointment_bp.route('/', methods=['POST'])
@login_required 
def create():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    try:
        # Pega dados do JSON enviado pelo JS
        new_appt = AppointmentService.create_appointment(
            professional_user_id=data.get('professional_id'),
            service_text=data.get('service_text'), # Texto livre
            start_str=data.get('date'),
            patient_user_id=data.get('patient_id'),
            guest_name=data.get('guest_name'),
            guest_phone=data.get('guest_phone')
        )
        
        return jsonify({
            "message": "Agendamento criado com sucesso!",
            "id": new_appt.id
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Erro Interno: {e}")
        return jsonify({"error": "Erro interno do servidor."}), 500


@appointment_bp.route('/list', methods=['GET'])
@login_required
def list_view():
    current_user_id = session['user']['id']
    
    # 1. Busca Profissional Logado (Para preencher o campo fixo)
    current_pro = Professional.query.filter_by(user_id=current_user_id).first()
    
    # 2. Busca Agendamentos (Ordenados por data)
    appointments = Appointment.query.order_by(Appointment.start_at.desc()).all()
    
    # 3. Busca Pacientes (Para o Select)
    patients = User.query.filter_by(role='patient').all()

    return render_template(
        'appointments.html', 
        appointments=appointments, 
        patients=patients,
        current_pro=current_pro
    )