from app.models.user_models import User
from app.models.professional import Professional
from app.db import db
from flask_jwt_extended import create_access_token # <--- ISSO É ESSENCIAL

class AuthService:
    @staticmethod
    def register_user(data):
        try:
            # 1. Validação de dados básicos
            email = data.get('email')
            name = data.get('name')
            password = data.get('password')
            role = data.get('role', 'patient')
            crm = data.get('crm')

            if not email or not name or not password:
                return {"error": "Nome, email e senha são obrigatórios."}, 400

            # 2. Verifica se email já existe
            if User.query.filter_by(email=email).first():
                return {"error": "Este email já está cadastrado."}, 409

            # 3. Cria o usuário (User)
            new_user = User(
                name=name,
                email=email,
                role=role,
                phone=data.get('phone') # Adicionei caso venha do form
            )
            new_user.set_password(password) # Hash da senha
            
            db.session.add(new_user)
            db.session.commit() # Gera o ID do user
            
            # 4. (NOVO) Se for Dentista, cria o perfil Profissional
            if role == 'dentist' or role == 'professional':
                new_pro = Professional(
                    user_id=new_user.id,
                    crm=crm,
                    color="#007bff" # Cor padrão
                )
                db.session.add(new_pro)
                db.session.commit()
            
            return {"message": "Usuário criado com sucesso", "user": new_user.to_dict()}, 201

        except Exception as e:
            db.session.rollback()
            return {"error": f"Erro no servidor: {str(e)}"}, 500

    @staticmethod
    def login_user(data):
        try:
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return {"error": "Email e senha são obrigatórios"}, 400

            # 1. Busca usuário
            user = User.query.filter_by(email=email).first()
            
            # 2. Verifica senha
            if not user or not user.check_password(password):
                return {"error": "Email ou senha incorretos."}, 401
                
            # 3. Gera Token REAL (Isso estava faltando na versão anterior)
            # O identity deve ser String para evitar erros em alguns parsers JSON
            access_token = create_access_token(
                identity=str(user.id), 
                additional_claims={"role": user.role}
            )
            
            return {
                "message": "Login realizado com sucesso",
                "access_token": access_token, # Token JWT válido
                "user": user.to_dict()
            }, 200

        except Exception as e:
            return {"error": f"Erro interno: {str(e)}"}, 500