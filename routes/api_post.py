from flask import redirect, Blueprint, request, jsonify
from controllers.comprador_controller import Compradores
from controllers.vendas_controller import Vendas
from data.connection_controller import Connection
from controllers.materiais_controller import Materiais
from controllers.cooperados_controller import Catadores
from controllers.avaliacoes_controller import Avaliacoes
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

@api_post.route("/finalizar-avaliacao-pendente/<int:id_avaliacao_pendente>", methods=["POST"])
def finalizar_avaliacao_pendente(id_avaliacao_pendente):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Token não fornecido'}), 401



    conn = Connection('local')

    try:
        # 1. Validar o Token e Permissão
        db = conn.connection_db
        from controllers.tokens_controller import Tokens
        from controllers.usuarios_controller import Usuarios
        data_token = Tokens(db).validar(token)
        if not data_token:
            conn.close()
            return jsonify({'error': 'Token inválido ou expirado'}), 401

        id_usuario = data_token['id_usuario']
        usuario_info = Usuarios(db).get(id_usuario)

        if not usuario_info or usuario_info['tipo'] not in ['cooperativa', 'cooperado']:
            conn.close()
            return jsonify({'error': 'Acesso não autorizado'}), 403

        # 2. Receber dados da avaliação
        dados_avaliacao = request.get_json()
        if not dados_avaliacao:
            return jsonify({'error': 'Dados da avaliação não fornecidos'}), 400

        # 3. Finalizar avaliação pendente
        avaliacoes_controller = Avaliacoes(db)
        sucesso = avaliacoes_controller.finalizar_avaliacao_pendente(id_avaliacao_pendente, dados_avaliacao)

        if sucesso:
            conn.close()
            return jsonify({'status': 'sucesso', 'mensagem': 'Avaliação finalizada com sucesso!'}), 200
        else:
            conn.close()
            return jsonify({'error': 'Erro ao finalizar avaliação'}), 500

    except Exception as e:
        if conn: conn.close()
        print(f"Erro em /finalizar-avaliacao-pendente: {e}")
        return jsonify({'error': 'Erro interno no servidor'}), 500
