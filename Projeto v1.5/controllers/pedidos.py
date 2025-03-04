from flask import Blueprint, render_template, request, redirect, url_for
from models.config import conectar

# Criando um Blueprint para as rotas
bp = Blueprint('pedidos', url_prefix="/pedidos", template_folder="templates", import_name=__name__)

# 📌 Listar Pedidos
@bp.route('/')
def listar_pedidos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, c.nome, p.data_pedido, p.valor_total 
        FROM pedidos p
        JOIN clientes c ON p.cliente_id = c.id
        ORDER BY p.data_pedido DESC
    """)
    pedidos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('pedidos.html', pedidos=pedidos)

# 📌 Adicionar Pedido
@bp.route('/adicionar', methods=['GET', 'POST'])
def adicionar_pedido():
    conn = conectar()
    cursor = conn.cursor()

    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        cursor.execute("INSERT INTO pedidos (cliente_id, valor_total) VALUES (%s, 0)", (cliente_id,))
        pedido_id = cursor.lastrowid
        conn.commit()
        return redirect(url_for('pedidos.editar_pedido', id=pedido_id))

    cursor.execute("SELECT id, nome FROM clientes ORDER BY nome ASC")
    clientes = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('adicionar_pedido.html', clientes=clientes)

# 📌 Editar Pedido (Adicionar Produtos)
@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_pedido(id):
    conn = conectar()
    cursor = conn.cursor()

    if request.method == 'POST':
        produto_id = request.form['produto_id']
        quantidade = int(request.form['quantidade'])

        # Obtém o preço e o estoque do produto
        cursor.execute("SELECT preco, estoque FROM produtos WHERE id = %s", (produto_id,))
        produto = cursor.fetchone()
        preco, estoque_atual = produto

        # Verifica se há estoque suficiente
        if estoque_atual < quantidade:
            return f"Erro: Estoque insuficiente para o produto (Disponível: {estoque_atual})"

        total = preco * quantidade

        # Adiciona o produto ao pedido
        cursor.execute("INSERT INTO pedidos_produtos (pedido_id, produto_id, quantidade) VALUES (%s, %s, %s)",
                       (id, produto_id, quantidade))

        # Atualiza o valor total do pedido
        cursor.execute("UPDATE pedidos SET valor_total = valor_total + %s WHERE id = %s", (total, id))

        # Atualiza o estoque do produto
        cursor.execute("UPDATE produtos SET estoque = estoque - %s WHERE id = %s", (quantidade, produto_id))

        conn.commit()

    # Obtém detalhes do pedido
    cursor.execute("""
        SELECT p.id, c.nome, p.data_pedido, p.valor_total 
        FROM pedidos p
        JOIN clientes c ON p.cliente_id = c.id
        WHERE p.id = %s
    """, (id,))
    pedido = cursor.fetchone()

    # Obtém produtos disponíveis
    cursor.execute("SELECT id, nome, preco, estoque FROM produtos ORDER BY nome ASC")
    produtos = cursor.fetchall()

    # Obtém produtos já adicionados ao pedido
    cursor.execute("""
        SELECT pr.id, pr.nome, pp.quantidade, pr.preco 
        FROM pedidos_produtos pp
        JOIN produtos pr ON pp.produto_id = pr.id
        WHERE pp.pedido_id = %s
    """, (id,))
    itens_pedido = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('editar_pedido.html', pedido=pedido, produtos=produtos, itens_pedido=itens_pedido)


# 📌 Excluir Pedido
@bp.route('/excluir/<int:id>')
def excluir_pedido(id):
    conn = conectar()
    cursor = conn.cursor()

    # Remove os produtos do pedido antes de excluir o pedido
    cursor.execute("DELETE FROM pedidos_produtos WHERE pedido_id = %s", (id,))
    cursor.execute("DELETE FROM pedidos WHERE id = %s", (id,))

    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('pedidos.listar_pedidos'))
