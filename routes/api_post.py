from flask import redirect, Blueprint, request, jsonify
from controllers.comprador_controller import Compradores
from controllers.vendas_controller import Vendas
from data.connection_controller import Connection
import json
api_post = Blueprint('api_post', __name__, url_prefix="/post")

@api_post.route("/catador", methods=["POST"])
def cadastrar_catador():
    cpf = request.form.get("cpf")
    nome = request.form.get("nome")
    telefone = request.form.get("telefone")
    data_nascimento = request.form.get("data")
    return redirect("/login")

@api_post.route("/dados-venda", methods=["POST"])
def postar_dados_de_venda():
    dados_recebidos = request.get_json()
    conn = Connection('local')
    processar_venda = Vendas(conn.connection_db).registrar_nova_venda(2, dados_recebidos)
    
    return jsonify({"status": "sucesso", "mensagem": "Dados da venda recebidos!"}), 200

@api_post.route("/dados-comprador", methods=["POST"])
def postar_dados_comprador():
    conn = Connection('local')
    dados_recebidos = request.get_json()
    dados = json.loads(dados_recebidos)
    Compradores(conn.connection_db).create(str(dados))
    return({"status":"sucesso", "mensagem":"Dados do comprador recebidos"})

# eu que fiz samuel corrija

@api_post.route("cadastrar-sinonimo", methods=["POST"])
def registrar_sinonimo():
    data = request.get_json()

    categoria = data.get('categoria')
    nome_padrao = data.get('nome_padrao')
    sinonimo = data.get('sinonimo')

    if not all([categoria, nome_padrao, sinonimo]):
        return jsonify({'message': 'Faltam dados para registrar o sinônimo.'}), 400
    

    # tem que colocar os dados nossos certinho
    try:
        conn = Connection('local')
        cursor = conn.cursor()

        query = """
            INSERT INTO sinonimos (categoria, nome_padrao, sinonimo)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (categoria, nome_padrao, sinonimo))
        conn.commit()

        return jsonify({'message': 'Sinônimo registrado com sucesso!'}), 200

    except mysql.connector.Error as err:
        print("Erro MySQL:", err)
        return jsonify({'message': 'Erro ao salvar no banco de dados.'}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
