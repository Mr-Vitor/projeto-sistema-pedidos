from flask import Flask, render_template
from controllers.clientes import bp as cliente
from controllers.produtos import bp as produto
from controllers.pedidos import bp as pedido
from controllers.relatorios import bp as relatorio
from flask_login import LoginManager, login_required, current_user
from models.models import Usuario

# Inicializa a aplicação Flask
app = Flask(__name__)
app.secret_key = 'chave_secreta_segura'  # Altere para um valor seguro

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

# Rota inicial
@app.route('/')
@login_required
def index():
    return render_template('index.html')

# Executa o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
