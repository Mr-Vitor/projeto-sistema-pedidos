from werkzeug.security import generate_password_hash
from models.config import conectar

def cria_adm():
    conn = conectar()
    cursor = conn.cursor()

    # Dados do usuário admin
    nome = "Admin"
    email = "admin@email.com"
    senha = "password"
    senha_hash = generate_password_hash(senha)  # Gera o hash seguro
    tipo = "admin"

    # Insere no banco de dados
    cursor.execute("INSERT INTO usuarios (nome, email, senha, tipo) VALUES (%s, %s, %s, %s)",
                (nome, email, senha_hash, tipo))
    conn.commit()

    cursor.close()
    conn.close()

    print("Usuário administrador criado com sucesso!")

cria_adm()