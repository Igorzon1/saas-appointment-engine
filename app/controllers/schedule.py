from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from app.models.professional import Professional, WorkingSchedule
from app.db import db
from app.services.decorators import login_required, role_required
from datetime import datetime

# Blueprint específico para agenda
bp = Blueprint("schedule", __name__, template_folder="../views/templates")

ALLOWED_ROLES = ['dentist', 'clinic', 'professional']

@bp.route("/settings", methods=["GET"])
@login_required
@role_required(ALLOWED_ROLES)
def view_settings():
    """Exibe a tela para editar os horários"""
    user_id = session['user']['id']
    pro = Professional.query.filter_by(user_id=user_id).first()
    
    # Ordena por dia da semana (0=Dom, 1=Seg...) e hora de inicio
    schedules = WorkingSchedule.query.filter_by(professional_id=pro.id)\
        .order_by(WorkingSchedule.day_of_week, WorkingSchedule.start_time).all()

    return render_template("schedule_settings.html", schedules=schedules, pro=pro)


@bp.route("/settings/update", methods=["POST"])
@login_required
@role_required(ALLOWED_ROLES)
def update_settings():
    """Recebe o formulário e recria a agenda"""
    user_id = session['user']['id']
    pro = Professional.query.filter_by(user_id=user_id).first()

    # 1. Atualiza a cor (se quiser mudar)
    new_color = request.form.get('color')
    if new_color:
        pro.color = new_color

    # 2. LIMPEZA TOTAL: Remove horários antigos para salvar os novos
    # Isso evita duplicidade e lógica complexa de update
    WorkingSchedule.query.filter_by(professional_id=pro.id).delete()

    # 3. Pega as listas enviadas pelo HTML
    # O HTML vai mandar arrays: days[], starts[], ends[]
    days = request.form.getlist('days[]')
    starts = request.form.getlist('starts[]')
    ends = request.form.getlist('ends[]')

    # 4. Cria os novos horários
    for i in range(len(days)):
        # Ignora linhas vazias se houver
        if not days[i] or not starts[i] or not ends[i]:
            continue

        new_schedule = WorkingSchedule(
            professional_id=pro.id,
            day_of_week=int(days[i]),
            start_time=datetime.strptime(starts[i], "%H:%M").time(),
            end_time=datetime.strptime(ends[i], "%H:%M").time()
        )
        db.session.add(new_schedule)

    db.session.commit()
    flash("Agenda atualizada com sucesso!", "success")
    return redirect(url_for("schedule.view_settings"))