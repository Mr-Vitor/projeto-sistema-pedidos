import mysql.connector

# Configuração do banco de dados
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "pedido_gestao"
}

# Função para conectar ao banco de dados
def conectar():
    return mysql.connector.connect(**DB_CONFIG)

