from app.models import User
from app.db import db
from flask_jwt_extended import create_access_token

class AuthService:
    @staticmethod
    def register_user(data):
        # 1. Verifica se email já existe
        if User.query.filter_by(email=data['email']).first():
            return {"error": "Email já cadastrado"}, 400

        # 2. Cria o usuário (Define se é 'patient' ou 'professional' aqui)
        new_user = User(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            role=data.get('role', 'patient') # Padrão é paciente
        )
        new_user.set_password(data['password']) # Hash automático
        
        db.session.add(new_user)
        db.session.commit()
        
        return {"message": "Usuário criado com sucesso", "user": new_user.to_dict()}, 201

    @staticmethod
    def login_user(data):
        # 1. Busca usuário
        user = User.query.filter_by(email=data['email']).first()
        
        # 2. Verifica senha
        if not user or not user.check_password(data['password']):
            return {"error": "Email ou senha inválidos"}, 401
            
        # 3. Gera Token (Colocamos o ID e a Role dentro do token)
        access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
        
        return {
            "message": "Login realizado",
            "access_token": access_token,
            "user": user.to_dict()
        }, 200