from flask import Blueprint, render_template, request, redirect, url_for
from models.config import conectar

# Criando um Blueprint para as rotas
bp = Blueprint('produtos', url_prefix="/produtos", template_folder="templates", import_name=__name__)

# 📌 Listar Produtos
@bp.route('/')
def listar_produtos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, descricao, preco, estoque FROM produtos ORDER BY nome ASC")
    produtos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('produtos.html', produtos=produtos)

# 📌 Adicionar Produto
@bp.route('/adicionar', methods=['GET', 'POST'])
def adicionar_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = request.form['preco']
        estoque = request.form['estoque']

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO produtos (nome, descricao, preco, estoque) VALUES (%s, %s, %s, %s)",
                       (nome, descricao, preco, estoque))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('produtos.listar_produtos'))

    return render_template('adicionar_produto.html')

# 📌 Editar Produto
@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_produto(id):
    conn = conectar()
    cursor = conn.cursor()

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = request.form['preco']
        estoque = request.form['estoque']

        cursor.execute("UPDATE produtos SET nome=%s, descricao=%s, preco=%s, estoque=%s WHERE id=%s",
                       (nome, descricao, preco, estoque, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('produtos.listar_produtos'))

    cursor.execute("SELECT id, nome, descricao, preco, estoque FROM produtos WHERE id = %s", (id,))
    produto = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('editar_produto.html', produto=produto)

# 📌 Excluir Produto
@bp.route('/excluir/<int:id>')
def excluir_produto(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('produtos.listar_produtos'))
