from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from app.services.auth_service import AuthService
from app.services.decorators import logout_required

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
@logout_required
def register_view():
    if request.method == 'POST':
        response, status = AuthService.register_user(request.form)
        
        if status == 201:
            flash("Cadastro realizado! Faça login.", "success") # <--- MENSAGEM
            return redirect(url_for('auth.login_view'))
        else:
            flash(response.get('error'), "error") # <--- MENSAGEM DE ERRO
            # Não use redirect aqui em caso de erro, senão perde os dados do form
            return render_template('register.html')
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login_view():
    if request.method == 'POST':
        response, status = AuthService.login_user(request.form)
        
        if status == 200:
            session.permanent = True # Mantém logado mesmo se fechar o browser
            session['user'] = response['user']
            # Se quiser usar token para chamadas futuras via API:
            session['access_token'] = response['access_token'] 
            
            flash(f"Bem-vindo, {response['user']['name']}!", "success")
            return redirect(url_for('dashboard.index')) # Rota principal (verifique o nome!)
        else:
            flash(response.get('error'), "error")
    
    return render_template('login.html')

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for('auth.login_view'))