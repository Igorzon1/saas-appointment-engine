from flask import Blueprint, request, render_template, redirect, url_for

bp = Blueprint("patients", __name__, template_folder="../views/templates")

@bp.route("/", methods=["GET"])
def index():
    # Busca todos os pacientes ordenados pelo nome
    patients_list = Patient.query.order_by(Patient.name).all()
    return render_template("patients.html", patients=patients_list)

@bp.route("/create", methods=["POST"])
def create():
    data = request.form
    
    # Criar novo paciente
    new_patient = Patient(
        name=data.get("name"),
        email=data.get("email"),
        phone=data.get("phone"),
        cpf=data.get("cpf")
    )
    
    db.session.add(new_patient)
    db.session.commit()
    
    return redirect(url_for("patients.index"))