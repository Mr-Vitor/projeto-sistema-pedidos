from werkzeug.security import generate_password_hash
from models.config import conectar

def cria_adm():
    conn = conectar()
    cursor = conn.cursor()

    # Verifica se já existe um admin no banco
    cursor.execute("SELECT id FROM usuarios WHERE tipo = 'admin' and email = 'admin@email.com' LIMIT 1")
    admin_existente = cursor.fetchone()

    if not admin_existente:  # Se não houver admin, cria um
        nome = "Admin"
        email = "admin@email.com"
        senha = "password"
        senha_hash = generate_password_hash(senha)  # Gera o hash seguro
        tipo = "admin"

        cursor.execute("INSERT INTO usuarios (nome, email, senha, tipo) VALUES (%s, %s, %s, %s)",
                       (nome, email, senha_hash, tipo))
        conn.commit()


    cursor.close()
    conn.close()
