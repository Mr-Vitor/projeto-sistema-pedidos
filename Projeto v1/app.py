from flask import Flask, render_template , url_for, request, redirect, flash
from datetime import datetime
import mysql.connector


app = Flask(__name__)

class Banco():
    def __init__(self):    
        self.conn = mysql.connector.connect(
                host = "localhost",
                user = "root",
                password = "4114",
                database = "db_projeto" #VER SE O NOME DO BANCO ESTÁ DE ACORDO
                

        )
## CADASTRA OS CLIENTES
    def cadastrar_cliente(self, nome, endereco, email, telefone):
            self.cursor = self.conn.cursor()
            self.cursor.execute("""SELECT COUNT(cli_id) FROM tb_clientes 
                                WHERE cli_email=%s""", (email,)) ## VÊ SE TEM ALGUM OUTRO CLIENTE COM ESSE NOME
            resposta=self.cursor.fetchone()
            if resposta[0]==0:    ## SE NÃO TEM, ELE ADICIONA OS VALORES
                self.cursor.execute("""INSERT INTO tb_clientes(cli_nome, cli_endereco ,cli_email, cli_telefone) 
                        VALUES (%s, %s, %s, %s)""", (nome, endereco, email, telefone))
                self.conn.commit()
                self.cursor.close()
                return redirect(url_for('cadastrar_clientes'))
            self.cursor.close()
            return redirect(url_for('cadastrar_clientes'))
## CADASTRA OS PRODUTOS
    def cadastrar_produto(self, nome, preco, descricao, estoque, categoria, data):
            self.cursor = self.conn.cursor()
            self.cursor.execute("""SELECT COUNT(pro_id) FROM tb_produtos 
                                WHERE pro_nome=%s""", (nome,)) ## VÊ SE TEM ALGUM OUTRO PRODUTO COM ESSE NOME
            resposta=self.cursor.fetchone()
            if resposta[0]==0:    
                self.cursor.execute("""INSERT INTO tb_produtos(pro_nome, pro_preco, pro_descricao, pro_estoque, pro_categoria, pro_data_cadastro) 
                        VALUES (%s, %s, %s, %s, %s, %s)""", (nome, preco, descricao, estoque, categoria, data))   ## SE NÃO TEM, ELE ADICIONA OS VALORES
                self.conn.commit()
                self.cursor.close()
                return redirect(url_for('cadastrar_produtos'))
            self.cursor.close()
            return redirect(url_for('cadastrar_produtos'))
## CADASTRA OS PEDIDOS
    def cadastrar_pedido(self, nome, email, senha):
            self.cursor = self.conn.cursor()
            self.cursor.execute("""SELECT COUNT(cli_id) FROM tb_clientes 
                                WHERE cli_email=%s""", (email,)) ## LEMBRAR DE MUDAR O NOME DA TABELA
            resposta=self.cursor.fetchone()
            if resposta[0]==0:    
                self.cursor.execute("""INSERT INTO tb_clientes(cli_nome, cli_endereco ,cli_email, cli_telefone) 
                        VALUES (%s, %s, %s, %s)""", (nome, endereco, email, telefone)) ## LEMBRAR DE MUDAR O NOME DA TABELA 
                self.conn.commit()
                self.cursor.close()
                return redirect(url_for('cadastrar_clientes'))
            self.cursor.close()
            return redirect(url_for('cadastrar_clientes'))
## LISTA CLIENTES
    def listar_clientes_ped(self):
        cards=""
        self.cursor=self.conn.cursor()
        self.cursor.execute("""SELECT * FROM tb_clientes""")
        result=self.cursor.fetchall()

        if result != None:
            for i in result:
                card=f"""
                <li>
                    <h3>{i[1]}</h3>
                    <ul>
                        <li>E-mail: {i[3]}</li>
                        <li>Telefone: {i[4]}</li>
                        <li>Endereço: {i[2]}</li>
                        <li class="bottons">
                            <form style="display: inline;" action="/list_pro_ped" method="post">
                                <input style="visibility: hidden;" name="ped_acao" value="pedir"></input>
                                <button class="edit1" name="escolher_cli" value="{i[0]}">pedir com esse cliente</button>
                            </form>
                        </li>
                    </ul>
                </li>"""
                cards+=card
            self.cursor.close()
            return cards
        
    def listar_clientes(self):
        cards=""
        self.cursor=self.conn.cursor()
        self.cursor.execute("""SELECT * FROM tb_clientes""")
        result=self.cursor.fetchall()

        if result != None:
            for i in result:
                card=f"""
                <li>
                    <h3>{i[1]}</h3>
                    <ul>
                        <li>E-mail: {i[3]}</li>
                        <li>Telefone: {i[4]}</li>
                        <li>Endereço: {i[2]}</li>
                        <li class="bottons">
                            <form style="display: inline;" action="/cli_edit" method="post">
                                <button class="edit1" name="acao" value="{i[0]}">Editar</button>
                                </form>
                                <form style="display: inline;" action="/cli_del" method="post">
                                <button class="delete" name="acao" value="{i[0]}">Excluir</button>
                            </form>
                        </li>
                    </ul>
                </li>"""
                cards+=card
            self.cursor.close()
            return cards 

    def listar_produtos(self):
        self.cursor=self.conn.cursor()
        self.cursor.execute("""SELECT * FROM tb_produtos""")
        result=self.cursor.fetchall()
        cards=""
        
        if result != None:
            for i in result:
                card=f"""
                <li>
                    <h3>{i[1]}</h3>
                    <ul>
                        <li>Descrição: {i[3]}</li>
                        <li>Preço: {i[2]}</li> 
                        <li>Estoque: {i[4]}</li>
                        <li>numero de produtos pedidos:{i[7]}</li>
                        <form action="/list_pro_ped" method="post">
                            <input type="hidden" name="pedido_id" value="{{ pedido_id }}">
    <input type="hidden" name="cliente_id" value="{{ cliente_id }}">
    <input type="number" name="quant_pro" placeholder="Ex.: +1 ou -2">
    <input type="hidden" name="ped_acao" value="quant">
    <input type="hidden" name="id_pro" value="{{ produto.id }}">
    <button type="submit">Adicionar</button>
                        </li>
                    </ul>
                </li>"""
                cards+=card
            self.cursor.close()
            return cards
        
    def deleter_cliente(self, id):
        self.cursor=self.conn.cursor()
        self.cursor.execute("""DELETE FROM tb_clientes 
                            WHERE cli_id=%s; """, (id,))
        self.conn.commit()

    def deletar_produto(self, id):
        self.cursor=self.conn.cursor()
        self.cursor.execute("""DELETE FROM tb_tarefas 
                            WHERE trf_id=%s; """, (id,))
        self.conn.commit()
        self.cursor.execute("""DELETE FROM tb_palavras_chave 
                            WHERE trf_id=%s; """, (id,))
        self.conn.commit()
    
    def deletar_pedido(self, id):
        self.cursor=self.conn.cursor()
        self.cursor.execute("""DELETE FROM tb_tarefas 
                            WHERE trf_id=%s; """, (id,))
        self.conn.commit()
        self.cursor.execute("""DELETE FROM tb_palavras_chave 
                            WHERE trf_id=%s; """, (id,))
        self.conn.commit()

    def listar_dados(self, id):
        self.cursor=self.conn.cursor()
        self.cursor.execute("""SELECT cli_nome, cli_endereco, cli_email, cli_telefone FROM tb_clientes
                            WHERE cli_id=%s""", (id,))
        dados=list(self.cursor.fetchone())
        result=[dados,id]
        return  result
    
    def editar_cliente(self, id, nome, endereco, email, telefone):
        self.cursor = self.conn.cursor()
        self.cursor.execute("""UPDATE tb_clientes SET cli_nome=%s, cli_endereco=%s, cli_email=%s, cli_telefone=%s
            Where cli_id=%s""", (nome, endereco, email, telefone, id))
        self.conn.commit()
        self.cursor.close()

    def editar_quant_pro(self, id, quant):
        self.cursor = self.conn.cursor()
        self.cursor.execute("""UPDATE tb_produtos SET pro_quantidade=%s
            Where pro_id=%s""", (quant, id))
        self.conn.commit()
        self.cursor.close()

    def criar_pedido(self, cliente_id):
        self.cursor = self.conn.cursor()
        self.cursor.execute("""INSERT INTO tb_pedidos(ped_cli_id, ped_data_criacao, ped_valor)
            VALUES (%s, NOW(), %s)""", (cliente_id,0))
        self.conn.commit()
        self.cursor.execute("SELECT LAST_INSERT_ID()")
        pedido_id = self.cursor.fetchone()[0]
        self.cursor.close()
        return pedido_id
    
    def adicionar_produto_pedido(self, pedido_id, produto_id, quantidade):
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            INSERT INTO tb_produtos_pedidos(prp_pro_id, prp_ped_id, quantidade)
            VALUES (%s, %s, %s)
        """, (pedido_id, produto_id, quantidade))
        self.conn.commit()
        self.cursor.close()
    
db = Banco()

@app.route("/", methods = ["GET","POST"])
def index():
    if request.method == "POST":
        pass
    else:
        
        return render_template("list_pedidos.html") 
## PÁGINA DE CADASTRAR CLIENTES
@app.route("/cli_cad", methods = ["GET","POST"])
def cadastrar_clientes():
    if request.method == "POST":
        nome = request.form['cli_nome']
        endereco = request.form['cli_endereco']
        email = request.form['cli_email']
        telefone = request.form['cli_telefone']
        return db.cadastrar_cliente(nome=nome, endereco=endereco, email=email, telefone=telefone)
    else:
        return render_template("cad_clientes.html")
## PÁGINA DE CADASTRAR PRODUTOS    
@app.route("/pro_cad", methods = ["GET","POST"])
def cadastrar_produtos():
    if request.method == "POST":
        data_cadastro = datetime.now().date()
        nome = request.form['pro_nome']
        preco = request.form['pro_preco']
        descricao = request.form['pro_descricao']
        estoque = request.form['pro_estoque']
        categoria = request.form['pro_categoria']
        return db.cadastrar_produto(nome=nome, descricao=descricao, categoria=categoria, preco=preco, estoque=estoque, data=data_cadastro)
    else:
        return render_template("cad_produtos.html")
    
@app.route('/list_cli_ped', methods = ["POST","GET"])
def listar_cli_ped():
    if request.method == "POST":
         pass
    cards=db.listar_clientes_ped()
    return render_template("cad_list_clientes.html", card=cards)

@app.route('/list_cli', methods = ["POST","GET"])
def listar_cli():
    if request.method == "POST":
         pass
    cards=db.listar_clientes()
    return render_template("list_clientes.html", card=cards)

@app.route('/list_pro_ped', methods = ["POST","GET"])
def listar_pro_ped():
    if request.method == "POST":
        if request.form["ped_acao"] == "pedir":
            cli_id = request.form["escolher_cli"]
            ped_id = db.criar_pedido(cli_id)
            cards=db.listar_produtos()
            return render_template("cad_list_produtos.html", card=cards, id=cli_id, ped_id=ped_id)
        elif request.form["ped_acao"] == "quant":
            id=request.form['id_pro']
            quant=request.form['quant_pro']
            db.editar_quant_pro(quant=quant, id=id)
            return redirect(url_for('listar_pro_ped'))
    cards = db.listar_produtos()
    return render_template("cad_list_produtos.html", card=cards)
        
@app.route('/cli_edit', methods=["POST","GET"])
def editar_cliente():
    if request.method == "POST":
        if request.form['acao'] == 'editar':
            id = request.form['cli_id']
            nome = request.form['cli_nome']
            endereco = request.form['cli_endereco']
            email = request.form['cli_email']
            telefone = request.form['cli_telefone']
            db.editar_cliente(id=id, nome=nome, endereco=endereco, email=email,telefone=telefone)
            return redirect(url_for('listar_cli'))
        else:
            dados=db.listar_dados(request.form['acao'])
            print(dados)
            return render_template('up_clientes.html', dado=dados[0],id=dados[1])


@app.route('/cli_del', methods=["POST","GET"])
def deletar_cliente():
    if request.method == "POST":
        id = request.form['acao']
        db.deleter_cliente(id)
    return redirect(url_for('listar_cli_ped'))

@app.route('/quant_pro', methods=["POST","GET"])
def quant_pro():
    if request.method=='post':
        id=request.form['id_pro']
        quant=request.form['quant_pr']
        db.editar_quant_pro(quant=quant, id=id)
        return redirect(url_for('listar_pro_ped', method='post'))
