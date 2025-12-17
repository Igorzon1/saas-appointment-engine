from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='../views/templates')

@auth_bp.route('/register', methods=['GET', 'POST'])
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
def login_view():
    if request.method == 'POST':
        data = request.form
        response, status = AuthService.login_user(data)
        
        if status == 200:
            # Aqui você pode salvar o token em uma sessão ou cookie
            return redirect(url_for('dashboard.index'))
        else:
            return render_template('login.html', error=response.get('error')), status
    
    return render_template('login.html')