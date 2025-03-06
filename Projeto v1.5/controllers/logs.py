from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from models.config import conectar

# Criando um Blueprint para as rotas
bp = Blueprint('logs', url_prefix="/logs", template_folder="templates", import_name=__name__)

# 📌 Logs
@bp.route('/')
@login_required
def listar_logs():
    if not current_user.is_admin():
        return "Acesso negado", 403

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT l.id, l.descricao, l.data_hora, u.nome 
        FROM logs l 
        JOIN usuarios u ON l.usuario_id = u.id
        ORDER BY l.data_hora DESC
    """)
    logs = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('usuarios/logs.html', logs=logs)