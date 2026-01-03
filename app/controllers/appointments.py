from flask import Blueprint, request, jsonify, render_template, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.appointment_models import Appointment
from app.models.user_models import User
from app.db import db
from datetime import datetime
from app.services.decorators import login_required

appointment_bp = Blueprint('appointments', __name__, url_prefix='/appointments')

@appointment_bp.route('/', methods=['POST'])
@login_required  # Protege - exige login
def create_appointment():
    # Pega o ID do token da sessão
    if 'user' not in session:
        return jsonify({"error": "Não autenticado"}), 401
    
    current_user_id = session['user']['id']
    data = request.get_json()
    
    # 1. Validar Dados
    if 'professional_id' not in data or 'date' not in data:
        return jsonify({"error": "Dados incompletos (professional_id e date obrigatórios)"}), 400

    # 2. Verifica se o dentista existe
    professional = User.query.filter_by(id=data['professional_id'], role='professional').first()
    if not professional:
        return jsonify({"error": "Profissional não encontrado"}), 404

    try:
        # 3. Cria o Agendamento
        new_appointment = Appointment(
            service_type=data.get('service_type', 'Consulta Geral'),
            start_at=datetime.strptime(data['date'], '%Y-%m-%d %H:%M'),
            status='scheduled',
            professional_id=professional.id,
            patient_id=current_user_id
        )
        
        db.session.add(new_appointment)
        db.session.commit()
        
        return jsonify({
            "message": "Agendamento realizado com sucesso",
            "data": new_appointment.to_dict()
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@appointment_bp.route('/list', methods=['GET'])
@login_required  # Protege - exige login
def list_view():
    # Busca todos os agendamentos para mostrar na lista
    appointments = Appointment.query.all()
    return render_template('appointments.html', appointments=appointments)