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
    
    ordem = request.args.get('ordem', 'asc').lower()  # Obtém o parâmetro da URL (padrão: asc)

    conn = conectar()
    cursor = conn.cursor()

    # Verifica se a ordem é válida (ascendente ou descendente)
    if ordem not in ['asc', 'desc']:
        ordem = 'asc'

    query = f"SELECT id, nome, email, tipo FROM usuarios ORDER BY nome {ordem}"
    cursor.execute(query)
    
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('usuarios/adicionar_usuario.html', usuarios=usuarios, ordem=ordem)


# 📌 Editar usuario
@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(id):
    conn = conectar()
    cursor = conn.cursor()

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']

        cursor.execute("UPDATE usuarios SET nome=%s, email=%s WHERE id=%s",
                       (nome, email, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('usuarios.adicionar_usuario'))

    cursor.execute("SELECT id, nome, email FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('usuarios/editar_usuario.html', usuario=usuario)

# 📌 Excluir Usuario
@bp.route('/excluir/<int:id>')
@login_required
def excluir_usuario(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('usuarios.adicionar_usuario'))


@bp.route('/filtrar', methods=['GET','POST'])
@login_required
def filtrar_usuario():
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


    filtros = {
        "nome": request.args.get('nome', '').strip(),
        "email": request.args.get('email', '').strip(),
        "tipo": request.args.get('tipo', '').strip()
    }

    conn = conectar()
    cursor = conn.cursor()

    # Dicionário mapeando os filtros para as condições SQL
    condicoes_sql = {
        "nome": "nome LIKE %s",
        "email": "email LIKE %s",
        "tipo": "tipo LIKE %s",
    }

    # Monta dinamicamente a query com os filtros preenchidos
    condicoes = [condicoes_sql[chave] for chave, valor in filtros.items() if valor]
    parametros = [f"%{valor}%" for chave, valor in filtros.items() if valor]

    query = "SELECT id, nome, email, tipo FROM usuarios"
    if condicoes:
        query += " WHERE " + " AND ".join(condicoes)
    query += " ORDER BY nome ASC"

    cursor.execute(query, parametros)
    usuario = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('usuarios/adicionar_usuario.html', usuarios=usuario, **filtros)
