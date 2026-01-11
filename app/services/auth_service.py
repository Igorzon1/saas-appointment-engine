from app.models.user_models import User
from app.models.professional import Professional
from app.db import db
from flask_jwt_extended import create_access_token

class AuthService:
    @staticmethod
    def register_user(data):
        try:
            # 1. Validação de dados básicos
            email = data.get('email')
            name = data.get('name')
            password = data.get('password')
            role = data.get('role', 'patient')
            
            # LÓGICA DE DOCUMENTO:
            # Se for Dentista pega CRM, se for Clínica pega CNPJ
            doc_identifier = data.get('crm')
            if role == 'clinic':
                doc_identifier = data.get('cnpj')

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
                phone=data.get('phone')
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit() # Gera o ID do user
            
            # 4. CRIAÇÃO DO PERFIL PROFISSIONAL / CLÍNICA
            # Aceitamos 'dentist', 'clinic' ou 'professional'
            if role in ['dentist', 'clinic', 'professional']:
                
                # Define cor: Azul para dentista, Verde para clínica
                agenda_color = "#28a745" if role == 'clinic' else "#007bff"
                
                new_pro = Professional(
                    user_id=new_user.id,
                    crm=doc_identifier, # Salva CRM ou CNPJ aqui
                    color=agenda_color
                )
                db.session.add(new_pro)
                db.session.commit()
            
            # O to_dict aqui já vai retornar tudo integrado graças à mudança no Model
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
                
            # 3. Gera Token REAL
            access_token = create_access_token(
                identity=str(user.id), 
                additional_claims={"role": user.role}
            )
            
            return {
                "message": "Login realizado com sucesso",
                "access_token": access_token,
                # O to_dict() aqui retorna {id, name, role, professional: {id, crm, color}}
                "user": user.to_dict() 
            }, 200

        except Exception as e:
            return {"error": f"Erro interno: {str(e)}"}, 500