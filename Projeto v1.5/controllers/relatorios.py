from flask import Blueprint, render_template, request, redirect, url_for
from models.config import conectar

# Criando um Blueprint para as rotas
bp = Blueprint('relatorios', url_prefix="/relatorios", template_folder="templates", import_name=__name__)

# 📌 Botões de Relatorios
@bp.route('/', methods=['GET', 'POST'])
def pg_relatorio():
    return render_template('relatorios/relatorios.html')


@bp.route('/total_pedidos_cliente', methods=['GET'])
def total_pedidos_cliente():
    cliente_id = request.args.get('cliente_id', '')
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    query_cliente = f"SELECT id, nome, email FROM clientes ORDER BY nome ASC"

    conn = conectar()
    cursor = conn.cursor()

    query = """
        SELECT SUM(valor_total) 
        FROM pedidos 
        WHERE cliente_id = %s AND data_pedido BETWEEN %s AND %s
    """
    cursor.execute(query, (cliente_id, data_inicio, data_fim))
    total = cursor.fetchone()[0] or 0  # Se não houver pedidos, retorna 0

    cursor.execute(query_cliente)
    clientes = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return render_template('relatorios/relatorio_total_pedidos.html', total=total,clientes=clientes, cliente_id=cliente_id, data_inicio=data_inicio, data_fim=data_fim)

@bp.route('/clientes_acima_500', methods=['GET'])
def clientes_acima_500():
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')

    conn = conectar()
    cursor = conn.cursor()

    query = """
        SELECT c.id, c.nome, SUM(p.valor_total) AS total_gasto
        FROM clientes c
        JOIN pedidos p ON c.id = p.cliente_id
        WHERE p.data_pedido BETWEEN %s AND %s
        GROUP BY c.id
        HAVING total_gasto > 500
        ORDER BY total_gasto DESC
    """
    cursor.execute(query, (data_inicio, data_fim))
    clientes = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return render_template('relatorios/relatorio_clientes_500.html', clientes=clientes, data_inicio=data_inicio, data_fim=data_fim)

@bp.route('/top_produtos', methods=['GET'])
def top_produtos():
    dias = request.args.get('dias', '7')  # Padrão: últimos 7 dias

    conn = conectar()
    cursor = conn.cursor()

    query = """
        SELECT pr.id, pr.nome, SUM(pp.quantidade) AS total_vendido
        FROM pedidos_produtos pp
        JOIN produtos pr ON pp.produto_id = pr.id
        JOIN pedidos p ON pp.pedido_id = p.id
        WHERE p.data_pedido >= NOW() - INTERVAL %s DAY
        GROUP BY pr.id
        ORDER BY total_vendido DESC
        LIMIT 10
    """
    cursor.execute(query, (dias,))
    produtos = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return render_template('relatorios/relatorio_top_produtos.html', produtos=produtos, dias=dias)

@bp.route('/produtos_nao_pedidos', methods=['GET'])
def produtos_nao_pedidos():
    dias = request.args.get('dias', '7')  # Padrão: últimos 7 dias

    conn = conectar()
    cursor = conn.cursor()

    query = """
        SELECT pr.id, pr.nome 
        FROM produtos pr
        WHERE pr.id NOT IN (
            SELECT DISTINCT pp.produto_id
            FROM pedidos_produtos pp
            JOIN pedidos p ON pp.pedido_id = p.id
            WHERE p.data_pedido >= NOW() - INTERVAL %s DAY
        )
        ORDER BY pr.nome ASC
    """
    cursor.execute(query, (dias,))
    produtos = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return render_template('relatorios/relatorio_produtos_nao_pedidos.html', produtos=produtos, dias=dias)
