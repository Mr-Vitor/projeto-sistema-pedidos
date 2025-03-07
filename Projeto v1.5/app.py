from flask import Flask, render_template
from controllers.clientes import bp as cliente
from controllers.produtos import bp as produto
from controllers.pedidos import bp as pedido
from controllers.relatorios import bp as relatorio
from controllers.auth import bp as auth
from controllers.usuarios import bp as usuario
from controllers.logs import bp as log
from flask_login import LoginManager, login_required, current_user
from models.models import Usuario
from models.config import conectar
from add_admin import cria_adm  


app = Flask(__name__)
app.secret_key = 'Trabalho_de_hugoat' 

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, email, senha, tipo FROM usuarios WHERE id = %s", (user_id,))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()
    if usuario:
        return Usuario(*usuario)
    return None


# Registra as rotas do arquivo routes.py
app.register_blueprint(cliente)
app.register_blueprint(produto)
app.register_blueprint(pedido)
app.register_blueprint(relatorio)
app.register_blueprint(auth)
app.register_blueprint(usuario)
app.register_blueprint(log)


cria_adm()


@app.route('/')
@login_required
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
