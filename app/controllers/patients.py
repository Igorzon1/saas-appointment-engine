from flask import Blueprint, request, render_template, redirect, url_for, flash, session, abort
import secrets
from app.models.user_models import User as Patient
from app.db import db
from app.services.decorators import login_required

bp = Blueprint("patients", __name__, template_folder="../views/templates")

@bp.route("/", methods=["GET"])
@login_required  # Protege - exige login
def index():
    # Apenas profissionais podem ver a lista de pacientes
    me = session.get('user')
    if not me or me.get('role') != 'professional':
        flash('Acesso negado', 'danger')
        return redirect(url_for('auth.login_view'))

    patients_list = Patient.query.filter_by(role='patient', dentist_id=me['id']).order_by(Patient.name).all()
    return render_template("patients.html", patients=patients_list)

@bp.route("/create", methods=["POST"])
@login_required  # Protege - exige login
def create():
    me = session.get('user')
    if not me or me.get('role') != 'professional':
        flash('Acesso negado', 'danger')
        return redirect(url_for('auth.login_view'))

    data = request.form

    # Normaliza email: transforma string vazia em None para permitir múltiplos NULL
    email = data.get("email") or None

    # Verifica duplicidade de e-mail apenas entre pacientes deste dentista
    if email and Patient.query.filter_by(email=email, dentist_id=me['id']).first():
        flash('E-mail já cadastrado no sistema', 'danger')
        return redirect(url_for('patients.index'))

    # Criar novo paciente associado ao dentista atual
    new_patient = Patient(
        name=data.get("name"),
        email=email,
        phone=data.get("phone"),
        cpf=data.get("cpf"),
        role='patient',
        dentist_id=me['id']
    )
    # Gera uma senha aleatória e armazena o hash para satisfazer a constraint
    random_password = secrets.token_urlsafe(12)
    new_patient.set_password(random_password)

    db.session.add(new_patient)
    db.session.commit()
    
    flash('Paciente cadastrado com sucesso', 'success')
    return redirect(url_for("patients.index"))


@bp.route('/<int:patient_id>/edit', methods=['GET'])
@login_required
def edit(patient_id):
    me = session.get('user')
    if not me or me.get('role') != 'professional':
        flash('Acesso negado', 'danger')
        return redirect(url_for('auth.login_view'))

    patient = Patient.query.get_or_404(patient_id)
    if patient.dentist_id != me['id']:
        abort(403)

    return render_template('patients_edit.html', patient=patient)


@bp.route('/<int:patient_id>/update', methods=['POST'])
@login_required
def update(patient_id):
    me = session.get('user')
    if not me or me.get('role') != 'professional':
        flash('Acesso negado', 'danger')
        return redirect(url_for('auth.login_view'))

    patient = Patient.query.get_or_404(patient_id)
    if patient.dentist_id != me['id']:
        abort(403)

    data = request.form
    new_email = data.get('email') or None
    # Checa se o novo e-mail já pertence a outro paciente do mesmo dentista
    if new_email and new_email != patient.email and Patient.query.filter(Patient.email == new_email, Patient.dentist_id == me['id'], Patient.id != patient.id).first():
        flash('E-mail já cadastrado no sistema', 'danger')
        return redirect(url_for('patients.index'))

    patient.name = data.get('name')
    patient.email = new_email
    patient.phone = data.get('phone')
    patient.cpf = data.get('cpf')

    db.session.commit()
    flash('Paciente atualizado', 'success')
    return redirect(url_for('patients.index'))


@bp.route('/<int:patient_id>/delete', methods=['POST'])
@login_required
def delete(patient_id):
    me = session.get('user')
    if not me or me.get('role') != 'professional':
        flash('Acesso negado', 'danger')
        return redirect(url_for('auth.login_view'))

    patient = Patient.query.get_or_404(patient_id)
    if patient.dentist_id != me['id']:
        abort(403)

    db.session.delete(patient)
    db.session.commit()
    flash('Paciente excluído', 'success')
    return redirect(url_for('patients.index'))