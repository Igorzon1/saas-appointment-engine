from flask import redirect, url_for, session
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps

def login_required(f):
    """Decorador que protege rotas exigindo login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verifica se há token na sessão
        if 'access_token' not in session:
            return redirect(url_for('auth.login_view'))
        return f(*args, **kwargs)
    return decorated_function

def logout_required(f):
    """Decorador que redireciona para dashboard se já está logado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Se tem token na sessão, redireciona para dashboard
        if 'access_token' in session:
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function