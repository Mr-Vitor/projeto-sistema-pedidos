from flask import Blueprint, render_template, request, redirect, url_for
from models.config import conectar

# Criando um Blueprint para as rotas
bp = Blueprint('clientes', url_prefix="/clientes", template_folder="templates", import_name=__name__)

# 📌 Listar Clientes
@bp.route('/')
def listar_clientes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, email, telefone, endereco FROM clientes ORDER BY nome ASC")
    clientes = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('clientes.html', clientes=clientes)

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

    return render_template('adicionar_cliente.html')

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
    return render_template('editar_cliente.html', cliente=cliente)

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
