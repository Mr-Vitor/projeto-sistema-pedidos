from flask import Blueprint, render_template, request, redirect, url_for
from models.config import conectar

# Criando um Blueprint para as rotas
bp = Blueprint('produtos', url_prefix="/produtos", template_folder="templates", import_name=__name__)

# 📌 Listar Produtos
@bp.route('/')
def listar_produtos():
    ordem = request.args.get('ordem', 'asc').lower()

    conn = conectar()
    cursor = conn.cursor()

    if ordem not in ['asc', 'desc']:
        ordem = 'asc'

    query = f"SELECT id, nome, descricao, preco, estoque FROM produtos ORDER BY nome {ordem}"
    cursor.execute(query)
    
    produtos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('produtos/produtos.html', produtos=produtos, ordem=ordem)

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

    return render_template('produtos/adicionar_produto.html')

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
    return render_template('produtos/editar_produto.html', produto=produto)

# 📌 Excluir Produto e Atualizar Pedidos
@bp.route('/excluir/<int:id>')
def excluir_produto(id):
    conn = conectar()
    cursor = conn.cursor()

    # Obtém os pedidos que contêm o produto a ser excluído
    cursor.execute("""
        SELECT pedido_id, quantidade FROM pedidos_produtos WHERE produto_id = %s
    """, (id,))
    pedidos_afetados = cursor.fetchall()

    for pedido_id, quantidade in pedidos_afetados:
        # Obtém o preço do produto antes de excluir
        cursor.execute("SELECT preco FROM produtos WHERE id = %s", (id,))
        preco = cursor.fetchone()[0]
        total_removido = preco * quantidade

        # Atualiza o valor total do pedido
        cursor.execute("UPDATE pedidos SET valor_total = valor_total - %s WHERE id = %s", (total_removido, pedido_id))

    # Remove o produto dos pedidos antes de excluí-lo do banco
    cursor.execute("DELETE FROM pedidos_produtos WHERE produto_id = %s", (id,))

    # Exclui o produto do banco
    cursor.execute("DELETE FROM produtos WHERE id = %s", (id,))

    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('produtos.listar_produtos'))


@bp.route('/filtrar', methods=['GET'])
def filtrar_produtos():
    filtros = {
        "nome": request.args.get('nome', '').strip(),
        "descricao": request.args.get('descricao', '').strip(),
        "preco_min": request.args.get('preco_min', '').strip(),
        "preco_max": request.args.get('preco_max', '').strip(),
        "estoque_min": request.args.get('estoque_min', '').strip(),
        "estoque_max": request.args.get('estoque_max', '').strip()
    }

    conn = conectar()
    cursor = conn.cursor()

    # Dicionário mapeando os filtros para as condições SQL
    condicoes_sql = {
        "nome": "nome LIKE %s",
        "descricao": "descricao LIKE %s",
        "preco_min": "preco >= %s",
        "preco_max": "preco <= %s",
        "estoque_min": "estoque >= %s",
        "estoque_max": "estoque <= %s"
    }

    # Filtra apenas os valores preenchidos e monta dinamicamente a query SQL
    condicoes = [condicoes_sql[chave] for chave, valor in filtros.items() if valor]
    parametros = [f"%{valor}%" if "LIKE" in condicoes_sql[chave] else valor for chave, valor in filtros.items() if valor]

    # Monta a query final
    query = "SELECT id, nome, descricao, preco, estoque FROM produtos"
    if condicoes:
        query += " WHERE " + " AND ".join(condicoes)
    query += " ORDER BY nome ASC"

    cursor.execute(query, parametros)
    produtos = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('produtos/produtos.html', produtos=produtos, **filtros)
