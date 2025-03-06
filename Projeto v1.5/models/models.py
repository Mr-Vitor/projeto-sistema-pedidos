from flask_login import UserMixin

class Usuario(UserMixin):
    def __init__(self, id, nome, email, senha, tipo):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha = senha
        self.tipo = tipo

    def is_admin(self):
        return self.tipo == 'admin'
