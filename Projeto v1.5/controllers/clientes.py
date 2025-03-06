from flask import Blueprint, render_template, request, redirect, url_for
from models.config import conectar

# Criando um Blueprint para as rotas
bp = Blueprint('clientes', url_prefix="/clientes", template_folder="templates", import_name=__name__)

# 📌 Listar Clientes
@bp.route('/')
def listar_clientes():
    ordem = request.args.get('ordem', 'asc').lower()  # Obtém o parâmetro da URL (padrão: asc)

    conn = conectar()
    cursor = conn.cursor()

    # Verifica se a ordem é válida (ascendente ou descendente)
    if ordem not in ['asc', 'desc']:
        ordem = 'asc'

    query = f"SELECT id, nome, email, telefone, endereco FROM clientes ORDER BY nome {ordem}"
    cursor.execute(query)
    
    clientes = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('clientes/clientes.html', clientes=clientes, ordem=ordem)


# 📌 Adicionar Cliente
@bp.route('/adicionar', methods=['GET', 'POST'])
def adicionar_cliente():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        endereco = request.form['endereco']

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clientes (nome, email, telefone, endereco) VALUES (%s, %s, %s, %s)",
                       (nome, email, telefone, endereco))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('clientes.listar_clientes'))

    return render_template('clientes/adicionar_cliente.html')

# 📌 Editar Cliente
@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    conn = conectar()
    cursor = conn.cursor()

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        endereco = request.form['endereco']

        cursor.execute("UPDATE clientes SET nome=%s, email=%s, telefone=%s, endereco=%s WHERE id=%s",
                       (nome, email, telefone, endereco, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('clientes.listar_clientes'))

    cursor.execute("SELECT id, nome, email, telefone, endereco FROM clientes WHERE id = %s", (id,))
    cliente = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('clientes/editar_cliente.html', cliente=cliente)

# 📌 Excluir Cliente
@bp.route('/excluir/<int:id>')
def excluir_cliente(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('clientes.listar_clientes'))


@bp.route('/filtrar', methods=['GET'])
def filtrar_clientes():
    filtros = {
        "nome": request.args.get('nome', '').strip(),
        "email": request.args.get('email', '').strip(),
        "telefone": request.args.get('telefone', '').strip(),
        "endereco": request.args.get('endereco', '').strip()
    }

    conn = conectar()
    cursor = conn.cursor()

    # Dicionário mapeando os filtros para as condições SQL
    condicoes_sql = {
        "nome": "nome LIKE %s",
        "email": "email LIKE %s",
        "telefone": "telefone LIKE %s",
        "endereco": "endereco LIKE %s"
    }

    # Monta dinamicamente a query com os filtros preenchidos
    condicoes = [condicoes_sql[chave] for chave, valor in filtros.items() if valor]
    parametros = [f"%{valor}%" for chave, valor in filtros.items() if valor]

    query = "SELECT id, nome, email, telefone, endereco FROM clientes"
    if condicoes:
        query += " WHERE " + " AND ".join(condicoes)
    query += " ORDER BY nome ASC"

    cursor.execute(query, parametros)
    clientes = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('clientes/clientes.html', clientes=clientes, **filtros)
