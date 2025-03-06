from flask import Flask, render_template
from controllers.clientes import bp as cliente
from controllers.produtos import bp as produto
from controllers.pedidos import bp as pedido
from controllers.relatorios import bp as relatorio

# Inicializa a aplicação Flask
app = Flask(__name__)

# Registra as rotas do arquivo routes.py
app.register_blueprint(cliente)
app.register_blueprint(produto)
app.register_blueprint(pedido)
app.register_blueprint(relatorio)

# Rota inicial
@app.route('/')
def index():
    return render_template('index.html')

# Executa o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
