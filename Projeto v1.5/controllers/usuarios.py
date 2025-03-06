from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from models.config import conectar

bp = Blueprint('usuarios', url_prefix="/usuarios", template_folder="templates", import_name=__name__)

# 📌 Rota para Adicionar Usuários (Apenas Administradores)
@bp.route('/', methods=['GET', 'POST'])
@login_required
def adicionar_usuario():
    if not current_user.is_admin():
        return "Acesso negado", 403

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        tipo = request.form['tipo']

        # Gerar hash da senha
        senha_hash = generate_password_hash(senha)

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nome, email, senha, tipo) VALUES (%s, %s, %s, %s)",
                       (nome, email, senha_hash, tipo))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Usuário cadastrado com sucesso!", "success")
        return redirect(url_for('usuarios.adicionar_usuario'))

    return render_template('usuarios/adicionar_usuario.html')
