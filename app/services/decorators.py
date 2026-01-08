from flask import redirect, url_for, session, flash
from functools import wraps

def login_required(f):
    """Apenas verifica se existe sessão válida."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verifica se o token ou user existe na sessão
        if 'user' not in session:
            flash("Faça login para acessar.", "error")
            return redirect(url_for('auth.login_view'))
        return f(*args, **kwargs)
    return decorated_function

def logout_required(f):
    """Chuta quem já está logado para o dashboard."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' in session:
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

# --- NOVO DECORATOR: CONTROLE DE PERMISSÃO ---
def role_required(allowed_roles):
    """
    Verifica se o usuário tem um dos cargos permitidos.
    Uso: @role_required(['dentist', 'admin'])
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 1. Garante que está logado primeiro
            if 'user' not in session:
                return redirect(url_for('auth.login_view'))
            
            user_role = session['user'].get('role')
            
            # 2. Verifica se o cargo está na lista permitida
            if user_role not in allowed_roles:
                flash("Acesso negado: Você não tem permissão para acessar esta área.", "danger")
                # Redireciona para o dashboard ou para onde fizer sentido
                return redirect(url_for('dashboard.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator