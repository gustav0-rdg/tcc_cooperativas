from flask import redirect, Blueprint, request, jsonify
from controllers.comprador_controller import Compradores
from controllers.vendas_controller import Vendas
from data.connection_controller import Connection
from controllers.materiais_controller import Materiais
import json
api_post = Blueprint('api_post', __name__, url_prefix="/post")

@api_post.route("/cooperado", methods=["POST"])
def cadastrar_cooperado():
    cpf = request.form.get("cpf")
    nome = request.form.get("nome")
    telefone = request.form.get("telefone")
    data_nascimento = request.form.get("data")
    return redirect("/login")

@api_post.route("/dados-venda", methods=["POST"])
def postar_dados_de_venda():

    
    dados_recebidos = request.get_json()
    conn = Connection('local')
    processar_venda = Vendas(conn.connection_db).registrar_nova_venda(dados_recebidos["id_cooperativa"], dados_recebidos)
    print(processar_venda)
    return jsonify({"status": "sucesso", "mensagem": "Dados da venda recebidos!"}), 200

@api_post.route("/dados-comprador", methods=["POST"])
def postar_dados_comprador():
    conn = Connection('local')
    dados_recebidos = request.get_json()
    dados = json.loads(dados_recebidos)
    Compradores(conn.connection_db).create(str(dados))
    return({"status":"sucesso", "mensagem":"Dados do comprador recebidos"})

# eu que fiz samuel corrija

@api_post.route("/cadastrar-sinonimo", methods=["POST"])
def registrar_sinonimo():
    data = request.get_json()

    nome_padrao = data.get('nome_padrao')
    sinonimo = data.get('sinonimo')
    # GRANDE AVISOOOO
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # TEM QUE COLOCAR O ID QUANDO FOR USAR USER
    id_cooperativa = 1
    

    if not all([nome_padrao, sinonimo]):
        return jsonify({'message': 'Faltam dados para registrar o sinônimo.'}), 400
    
    conn = Connection('local')

    resposta = Materiais(conn.connection_db).post_cadastrar_sinonimo(nome_padrao, sinonimo, id_cooperativa)
    return resposta

@api_post.route("/cadastrar-subtipo", methods=["POST"])
def cadastrar_subtipo():
    data = request.get_json()
    conn = Connection('local')
    resposta = Materiais(conn.connection_db).cadastrar_subtipo(data["nome_especifico"], data["id_material_base"])
    return resposta