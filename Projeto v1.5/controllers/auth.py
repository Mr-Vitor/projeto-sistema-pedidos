from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from models.models import Usuario
from models.config import conectar
import bcrypt

bp = Blueprint('auth', url_prefix="/auth", template_folder="templates", import_name=__name__)

# 📌 Rota de Login
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha'].encode('utf-8')

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, email, senha, tipo FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()

        if usuario and bcrypt.checkpw(senha, usuario[3].encode('utf-8')):
            user = Usuario(*usuario)
            login_user(user)
            return redirect(url_for('dashboard'))

        flash("E-mail ou senha inválidos", "danger")

    return render_template('login.html')

# 📌 Logout
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
