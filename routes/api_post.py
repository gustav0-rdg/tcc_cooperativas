from flask import redirect, Blueprint, request, jsonify
from controllers.comprador_controller import Compradores
from controllers.vendas_controller import Vendas
from data.connection_controller import Connection
from controllers.materiais_controller import Materiais
from controllers.cooperados_controller import Catadores
import json
api_post = Blueprint('api_post', __name__, url_prefix="/post")

@api_post.route("/post/cooperado", methods=["POST"])
def cadastrar_cooperado():
    try:
        data = request.get_json()

        nome = data.get("nome")
        email = data.get("email") or f"{data.get('cpf')}@cooperativa.org"
        senha = data.get("senha")
        cpf = data.get("cpf")
        telefone = data.get("telefone")
        endereco = data.get("endereco")
        cidade = data.get("cidade")
        estado = data.get("estado")
        id_cooperativa = int(data.get("id_cooperativa"))  # exemplo fixo

        conn = Connection('local')
        catadores = Catadores(conn.connection_db).create(
            nome=nome,
            email=email,
            senha=senha,
            id_cooperativa=id_cooperativa,
            cpf=cpf,
            telefone=telefone,
            endereco=endereco,
            cidade=cidade,
            estado=estado
        )

        if id_criado:
            return jsonify({"s"
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            "uccess": True, "id_catador": id_criado}), 201
        else:
            return jsonify({"success": False, "error": "Erro ao criar catador"}), 500

    except Exception as e:
        print(f"Erro em /post/cooperado: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

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
    conn = Connection('local')
    dados_recebidos = request.get_json()
    Compradores(conn.connection_db).create(str(dados_recebidos))
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