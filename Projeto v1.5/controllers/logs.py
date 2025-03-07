from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from models.config import conectar

# Criando um Blueprint para as rotas
bp = Blueprint('logs', url_prefix="/logs", template_folder="templates", import_name=__name__)

# 📌 Logs de Pedidos
@bp.route('/')
@login_required
def listar_logs():
    if not current_user.is_admin():
        return "Acesso negado", 403

    conn = conectar()
    cursor = conn.cursor()

    # Consulta ajustada para logs de pedidos
    cursor.execute("""
        SELECT lp.id_log, lp.operacao, lp.data_hora, u.nome AS usuario, 
                c.nome AS cliente, p.id AS pedido_id
        FROM logs_pedidos lp
        JOIN usuarios u ON lp.usuario_id = u.id
        JOIN clientes c ON lp.id_cliente = c.id
        LEFT JOIN pedidos p ON lp.id_pedido = p.id 
        ORDER BY lp.data_hora DESC;
    """)
    logs = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('logs/logs_pedidos.html', logs=logs)
