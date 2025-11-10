from flask import redirect, Blueprint, request, jsonify
from controllers.comprador_controller import Compradores
from controllers.vendas_controller import Vendas
from data.connection_controller import Connection
from controllers.materiais_controller import Materiais
from controllers.cooperados_controller import Catadores
import json

api_post = Blueprint('api_post', __name__, url_prefix="/post")

@api_post.route("/dados-venda", methods=["POST"])
def postar_dados_de_venda():

    try:
        dados_recebidos = request.get_json()
        conn = Connection('local')
        processar_venda = Vendas(conn.connection_db).registrar_nova_venda(dados_recebidos["id_cooperativa"], dados_recebidos)
        return jsonify({"status": "sucesso", "mensagem": "Dados da venda recebidos!"}), 200
    except Exception as e:
        print(e)
    finally:
        if conn:
            conn.close()

@api_post.route("/dados-comprador", methods=["POST"])
def postar_dados_comprador():
    try:
        conn = Connection('local')
        dados_recebidos = request.get_json()
        Compradores(conn.connection_db).create(str(dados_recebidos))
        return({"status":"sucesso", "mensagem":"Dados do comprador recebidos"})
    except Exception as e:
        print(e)
    finally:
        conn.close()

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
    try:
        data = request.get_json()
        conn = Connection('local')
        resposta = Materiais(conn.connection_db).cadastrar_subtipo(data["nome_especifico"], data["id_material_base"])
        return resposta
    except Exception as e:
        print(e)
    finally:
        conn.close()