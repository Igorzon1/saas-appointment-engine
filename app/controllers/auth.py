from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from app.services.auth_service import AuthService
from app.services.decorators import login_required, logout_required

auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='../views/templates')

@auth_bp.route('/register', methods=['GET', 'POST'])
@logout_required  # Protege - se logado, redireciona ao dashboard
def register_view():
    if request.method == 'POST':
        data = request.form
        response, status = AuthService.register_user(data)
        
        if status == 201:
            return redirect(url_for('auth.login_view'))
        else:
            return render_template('register.html', error=response.get('error')), status
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
@logout_required  # Protege - se logado, redireciona ao dashboard
def login_view():
    if request.method == 'POST':
        data = request.form
        response, status = AuthService.login_user(data)
        
        if status == 200:
            # Salva o token na sessão
            session['access_token'] = response['access_token']
            session['user'] = response['user']
            return redirect(url_for('dashboard.index'))
        else:
            return render_template('login.html', error=response.get('error')), status
    
    return render_template('login.html')

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('auth.login_view'))