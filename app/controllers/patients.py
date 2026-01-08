from flask import Blueprint, request, render_template, redirect, url_for, flash, session, abort
import secrets
from app.models.user_models import User
from app.db import db
from app.services.decorators import login_required, role_required

bp = Blueprint("patients", __name__, template_folder="../views/templates")

# Lista de permissões permitidas para gerenciar pacientes
ALLOWED_ROLES = ['dentist', 'professional', 'clinic']

@bp.route("/", methods=["GET"])
@login_required
@role_required(ALLOWED_ROLES)
def index():
    # Pega o ID do usuário logado (Dentista)
    current_user_id = session['user']['id']

    # Busca apenas pacientes deste dentista
    patients_list = User.query.filter_by(
        role='patient', 
        dentist_id=current_user_id
    ).order_by(User.name).all()
    
    return render_template("patients.html", patients=patients_list)

@bp.route("/create", methods=["POST"])
@login_required
@role_required(ALLOWED_ROLES)
def create():
    current_user_id = session['user']['id']
    data = request.form

    # Normaliza email
    email = data.get("email") or None

    # Verifica duplicidade apenas para pacientes deste dentista
    if email:
        existing = User.query.filter_by(email=email, dentist_id=current_user_id).first()
        if existing:
            flash('E-mail já cadastrado para outro paciente seu.', 'danger')
            return redirect(url_for('patients.index'))

    # Cria o paciente vinculado ao usuário logado
    new_patient = User(
        name=data.get("name"),
        email=email,
        phone=data.get("phone"),
        cpf=data.get("cpf"),
        role='patient',
        dentist_id=current_user_id # VÍNCULO IMPORTANTE
    )
    
    # Gera senha aleatória pois o model User exige senha
    random_password = secrets.token_urlsafe(12)
    new_patient.set_password(random_password)

    db.session.add(new_patient)
    db.session.commit()
    
    flash('Paciente cadastrado com sucesso!', 'success')
    return redirect(url_for("patients.index"))

@bp.route('/<int:patient_id>/edit', methods=['GET'])
@login_required
@role_required(ALLOWED_ROLES)
def edit(patient_id):
    current_user_id = session['user']['id']
    
    patient = User.query.get_or_404(patient_id)
    
    # Segurança: Garante que o paciente pertence ao dentista logado
    if patient.dentist_id != current_user_id:
        abort(403) # Forbidden

    return render_template('patients_edit.html', patient=patient)

@bp.route('/<int:patient_id>/update', methods=['POST'])
@login_required
@role_required(ALLOWED_ROLES)
def update(patient_id):
    current_user_id = session['user']['id']
    
    patient = User.query.get_or_404(patient_id)
    
    # Segurança
    if patient.dentist_id != current_user_id:
        abort(403)

    data = request.form
    new_email = data.get('email') or None

    # Verifica duplicidade de email na edição
    if new_email and new_email != patient.email:
        conflict = User.query.filter(
            User.email == new_email, 
            User.dentist_id == current_user_id, 
            User.id != patient.id
        ).first()
        
        if conflict:
            flash('Este e-mail já está em uso por outro paciente.', 'danger')
            return redirect(url_for('patients.index'))

    patient.name = data.get('name')
    patient.email = new_email
    patient.phone = data.get('phone')
    patient.cpf = data.get('cpf')

    db.session.commit()
    flash('Paciente atualizado com sucesso.', 'success')
    return redirect(url_for('patients.index'))

@bp.route('/<int:patient_id>/delete', methods=['POST'])
@login_required
@role_required(ALLOWED_ROLES)
def delete(patient_id):
    current_user_id = session['user']['id']
    
    patient = User.query.get_or_404(patient_id)
    
    # Segurança
    if patient.dentist_id != current_user_id:
        abort(403)

    db.session.delete(patient)
    db.session.commit()
    
    flash('Paciente removido.', 'success')
    return redirect(url_for('patients.index'))