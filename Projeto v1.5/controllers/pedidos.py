from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.config import conectar

# Criando um Blueprint para as rotas
bp = Blueprint('pedidos', url_prefix="/pedidos", template_folder="templates", import_name=__name__)

# 📌 Listar Pedidos
@bp.route('/')
@login_required
def listar_pedidos():
    ordem = request.args.get('ordem','desc').lower()

    conn = conectar()
    cursor = conn.cursor()
    
    if ordem not in ['asc','desc']:
        ordem = 'desc'

    query = f"""
        SELECT p.id, c.nome, p.data_pedido, p.valor_total 
        FROM pedidos p
        JOIN clientes c ON p.cliente_id = c.id
        ORDER BY p.data_pedido {ordem}
    """
    cursor.execute(query)

    pedidos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('pedidos/pedidos.html', pedidos=pedidos, ordem=ordem)

# 📌 Adicionar Pedido
@bp.route('/adicionar', methods=['GET', 'POST'])
@login_required
def adicionar_pedido():
    conn = conectar()
    cursor = conn.cursor()

    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        usuario_id = current_user.id
        cursor.execute("INSERT INTO pedidos (cliente_id, usuario_id, valor_total) VALUES (%s, %s, 0)", (cliente_id, usuario_id))
        pedido_id = cursor.lastrowid
        conn.commit()
        return redirect(url_for('pedidos.editar_pedido', id=pedido_id))

    cursor.execute("SELECT id, nome, email FROM clientes ORDER BY nome ASC")
    clientes = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('pedidos/adicionar_pedido.html', clientes=clientes)

@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
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
        flash(f"Erro: Estoque insuficiente para o produto (Disponível: {estoque_atual})", "danger")
        return redirect(url_for('editar_pedido', id=id))


        # Verifica se o produto já está no pedido
        cursor.execute("SELECT quantidade FROM pedidos_produtos WHERE pedido_id = %s AND produto_id = %s", (id, produto_id))
        existente = cursor.fetchone()

        if existente:
            # Atualiza a quantidade do produto no pedido
            nova_quantidade = existente[0] + quantidade
            cursor.execute("UPDATE pedidos_produtos SET quantidade = %s WHERE pedido_id = %s AND produto_id = %s",
                           (nova_quantidade, id, produto_id))
        else:
            # Adiciona o produto ao pedido
            cursor.execute("INSERT INTO pedidos_produtos (pedido_id, produto_id, quantidade) VALUES (%s, %s, %s)",
                           (id, produto_id, quantidade))

        # Atualiza o valor total do pedido utilizando a Function MySQL
        cursor.execute("UPDATE pedidos SET valor_total = calcular_valor_pedido(%s) WHERE id = %s", (id, id))

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
    return render_template('pedidos/editar_pedido.html', pedido=pedido, produtos=produtos, itens_pedido=itens_pedido)


# 📌 Atualizar ou Remover Produto do Pedido
@bp.route('/editar/<int:pedido_id>/produto/<int:produto_id>', methods=['POST'])
@login_required
def atualizar_produto_pedido(pedido_id, produto_id):
    conn = conectar()
    cursor = conn.cursor()

    if 'remover' in request.form:
        # Obtém a quantidade do produto antes de remover
        cursor.execute("SELECT quantidade FROM pedidos_produtos WHERE pedido_id = %s AND produto_id = %s",
                       (pedido_id, produto_id))
        quantidade_atual = cursor.fetchone()[0]

        # Atualiza o estoque do produto ao remover
        cursor.execute("UPDATE produtos SET estoque = estoque + %s WHERE id = %s", (quantidade_atual, produto_id))

        # Remove o produto do pedido
        cursor.execute("DELETE FROM pedidos_produtos WHERE pedido_id = %s AND produto_id = %s",
                       (pedido_id, produto_id))

        # Atualiza o valor total do pedido
        cursor.execute("SELECT preco FROM produtos WHERE id = %s", (produto_id,))
        preco = cursor.fetchone()[0]
        total_removido = preco * quantidade_atual
        cursor.execute("UPDATE pedidos SET valor_total = valor_total - %s WHERE id = %s", (total_removido, pedido_id))

    else:
        nova_quantidade = int(request.form['quantidade'])

        # Obtém o preço do produto e a quantidade atual no pedido
        cursor.execute("SELECT preco FROM produtos WHERE id = %s", (produto_id,))
        preco = cursor.fetchone()[0]

        cursor.execute("SELECT quantidade FROM pedidos_produtos WHERE pedido_id = %s AND produto_id = %s",
                       (pedido_id, produto_id))
        quantidade_atual = cursor.fetchone()[0]

        diferenca = nova_quantidade - quantidade_atual
        total_diferenca = preco * diferenca

        if nova_quantidade == 0:
            # Remove o produto se a quantidade for zerada
            cursor.execute("DELETE FROM pedidos_produtos WHERE pedido_id = %s AND produto_id = %s",
                           (pedido_id, produto_id))
            cursor.execute("UPDATE produtos SET estoque = estoque + %s WHERE id = %s", (quantidade_atual, produto_id))
            cursor.execute("UPDATE pedidos SET valor_total = valor_total - %s WHERE id = %s",
                           (preco * quantidade_atual, pedido_id))
        else:
            # Atualiza a quantidade do produto no pedido
            cursor.execute("UPDATE pedidos_produtos SET quantidade = %s WHERE pedido_id = %s AND produto_id = %s",
                           (nova_quantidade, pedido_id, produto_id))

            # Atualiza o valor total do pedido
            cursor.execute("UPDATE pedidos SET valor_total = valor_total + %s WHERE id = %s", (total_diferenca, pedido_id))


    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('pedidos.editar_pedido', id=pedido_id))

# 📌 Excluir Pedido
@bp.route('/excluir/<int:id>')
@login_required
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

@bp.route('/filtrar', methods=['GET'])
@login_required
def filtrar_pedidos():
    filtros = {
        "cliente": request.args.get('cliente', '').strip(),
        "data_min": request.args.get('data_min', '').strip(),
        "data_max": request.args.get('data_max', '').strip(),
        "valor_min": request.args.get('valor_min', '').strip(),
        "valor_max": request.args.get('valor_max', '').strip()
    }

    conn = conectar()
    cursor = conn.cursor()

    # Dicionário mapeando os filtros para as condições SQL
    condicoes_sql = {
        "cliente": "c.nome LIKE %s",
        "data_min": "p.data_pedido >= %s",
        "data_max": "p.data_pedido <= %s",
        "valor_min": "p.valor_total >= %s",
        "valor_max": "p.valor_total <= %s"
    }

    # Monta dinamicamente a query com os filtros preenchidos
    condicoes = [condicoes_sql[chave] for chave, valor in filtros.items() if valor]
    parametros = [f"%{valor}%" if "LIKE" in condicoes_sql[chave] else valor for chave, valor in filtros.items() if valor]

    query = """
        SELECT p.id, c.nome, p.data_pedido, p.valor_total 
        FROM pedidos p
        JOIN clientes c ON p.cliente_id = c.id
    """
    if condicoes:
        query += " WHERE " + " AND ".join(condicoes)
    query += " ORDER BY p.data_pedido DESC"

    cursor.execute(query, parametros)
    pedidos = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('pedidos/pedidos.html', pedidos=pedidos, **filtros)
