from flask import Blueprint, request, redirect, jsonify
from controllers.comprador_controller import Compradores
from controllers.materiais_controller import Materiais
from controllers.feedback_controller import Feedbacks
from controllers.usuarios_controller import Usuarios
from controllers.tokens_controller import Tokens
from controllers.cooperativa_controller import Cooperativa
from controllers.comentarios_controller import Comentarios
from controllers.vendas_controller import Vendas
from controllers.avaliacoes_controller import Avaliacoes
from data.connection_controller import Connection
api_get = Blueprint('api_get', __name__, url_prefix='/get')

@api_get.route("/compradores", methods=["GET"])
def get_compradores():
    try:
        conn = Connection('local')
        compradores = Compradores(conn.connection_db).get_all()
        return jsonify(compradores), 200
    except Exception as e:
        print(f"Erro ao buscar compradores: {e}")
        return jsonify({"erro": "Ocorreu um erro interno no servidor"}), 500
    finally:
        if conn:
            conn.close()
    
@api_get.route("/feedbacks", methods=["GET"])
def get_feedbacks():
    try:
        conn = Connection('local')
        feedbacks = Feedbacks(conn.connection_db).get_all()
        return jsonify(feedbacks), 200
    except Exception as e:
        print(f"Erro ao buscar feedbacks: {e}")
        return jsonify({"erro": "Ocorreu um erro interno no servidor"}), 500
    finally:
        if conn:
            conn.close()
    
@api_get.route("/materiais", methods=["GET"])
def get_materiais():
    """
    Rota para obter a lista completa de materiais do catálogo.
    """
    try:
        conn = Connection('local')
        materiais = Materiais(conn.connection_db).get_all()
        conn.close()
        return jsonify(materiais), 200
    except Exception as e:
        print(f"Erro ao buscar materiais: {e}")
        return jsonify({"erro": "Ocorreu um erro interno no servidor"}), 500
    finally:
        if conn:
            conn.close()

@api_get.route("/subtipos/<material_id>", methods=["GET"])
def get_subtipos_materiais(material_id):
    """
    Rota para obter a lista completa de materiais do catálogo.
    """
    try:
        conn = Connection('local')
        materiais = Materiais(conn.connection_db).get_subtipos(material_id)
        conn.close()
        return jsonify(materiais), 200
    except Exception as e:
        print(f"Erro ao buscar materiais: {e}")
        return jsonify({"erro": "Ocorreu um erro interno no servidor"}), 500
    finally:
        if conn:
            conn.close()
    
@api_get.route("/comprador/<material>/<subtipo>", methods=["GET"])
def get_by_material(material, subtipo):
    try:
        conn = Connection('local')
        compradores = Compradores(conn.connection_db).get_by_materials(material, subtipo)
        return jsonify(compradores), 200
    except Exception as e:
        print(f"Erro ao buscar ompradores por material: {e}")
        return jsonify({"erro":"Ocorreu um erro"}), 500
    finally:
        if conn:
            conn.close()

@api_get.route("/vendas/<id_cooperativa>")
def get_vendas_by_cooperativa(id_cooperativa):
    try:    
        conn = Connection('local')
        vendas = Vendas(conn.connection_db).get_by_coop(id_cooperativa)
        return jsonify(vendas),200
    except Exception as e:
        print(e)
        return jsonify({"erro":"falha ao buscar dados","error":e}),400
    finally:
        if conn:
            conn.close()

@api_get.route("/feedback-tags/<cnpj>", methods=["GET"])
def get_feedback_tags_vendedor(cnpj):
    try:
        conn = Connection('local')
        feedbacks_tags = Comentarios(conn.connection_db).get_feedback_tags(cnpj)
        return jsonify(feedbacks_tags), 200
    except Exception as e:
        print (e)
        return jsonify({"erro":"falha ao buscar dados"})
    finally:
        if conn:
            conn.close()

@api_get.route("/comentarios-livres/<cnpj>")
def get_comentarios(cnpj):
    try:
        conn = Connection('local')
        comentarios = Comentarios(conn.connection_db).get_comentarios(cnpj)
        return jsonify(comentarios), 200
    except Exception as e:
        return jsonify({"erro":"falha ao buscar dados","ERROR":e})
    finally:
        if conn:
            conn.close()

@api_get.route('/cooperativas-pendentes', methods=['GET'])
def get_cooperativas_pendentes():
    
    token_header = request.headers.get('Authorization')
    if not token_header:
        return jsonify({'error': 'Token não fornecido'}), 401

    try:
        token = token_header.split(" ")[1]
    except IndexError:
        return jsonify({'error': 'Token mal formatado'}), 401

    conn = Connection('local')
    
    try:
        # 1. Validar o Token e Permissão (reaproveitando a lógica de segurança)
        db = conn.connection_db
        data_token = Tokens(db).validar(token)
        if not data_token:
            conn.close()
            return jsonify({'error': 'Token inválido ou expirado'}), 401
        
        id_usuario = data_token['id_usuario']
        usuario_info = Usuarios(db).get(id_usuario)
        
        if not usuario_info or usuario_info['tipo'] not in ['gestor', 'root']:
            conn.close()
            return jsonify({'error': 'Acesso não autorizado'}), 403

        # 2. Buscar os dados (usando o método novo)
        cooperativas_pendentes = Cooperativa(db).get_pendentes_com_documentos()
        
        if cooperativas_pendentes is False:
            conn.close()
            return jsonify({'error': 'Erro ao buscar solicitações.'}), 500

        conn.close()
        return jsonify(cooperativas_pendentes), 200

    except Exception as e:
        if conn: conn.close()
        print(f"Erro em /cooperativas-pendentes: {e}")
        return jsonify({'error': 'Erro interno no servidor'}), 500

@api_get.route('/avaliacoes-pendentes/<id_cooperativa>', methods=['GET'])
def get_avaliacoes_pendentes(id_cooperativa):
    """
    Rota para obter as avaliações pendentes de uma cooperativa específica.
    """
    token_header = request.headers.get('Authorization')
    if not token_header:
        return jsonify({'error': 'Token não fornecido'}), 401
    print(token_header)

    conn = Connection('local')

    try:
        # 1. Validar o Token e Permissão
        db = conn.connection_db
        data_token = Tokens(db).validar(token_header)
        if not data_token:
            conn.close()
            return jsonify({'error': 'Token inválido ou expirado'}), 401

        id_usuario = data_token['id_usuario']
        usuario_info = Usuarios(db).get(id_usuario)

        if not usuario_info or usuario_info['tipo'] not in ['cooperativa', 'cooperado']:
            conn.close()
            return jsonify({'error': 'Acesso não autorizado'}), 403

        # 2. Buscar as avaliações pendentes
        avaliacoes_pendentes = Avaliacoes(db).get_avaliacoes_pendentes(int(id_cooperativa))

        conn.close()
        return jsonify(avaliacoes_pendentes), 200

    except Exception as e:
        if conn: conn.close()
        print(f"Erro em /avaliacoes-pendentes: {e}")
        return jsonify({'error': 'Erro interno no servidor'}), 500

@api_get.route('/avaliacao-pendente/<id_avaliacao_pendente>', methods=['GET'])
def get_avaliacao_pendente_por_id(id_avaliacao_pendente):
    """
    Rota para obter uma avaliação pendente específica por ID.
    """
    token_header = request.headers.get('Authorization')
    if not token_header:
        return jsonify({'error': 'Token não fornecido'}), 401

    conn = Connection('local')

    try:
        # 1. Validar o Token e Permissão
        db = conn.connection_db
        data_token = Tokens(db).validar(token_header)
        if not data_token:
            conn.close()
            return jsonify({'error': 'Token inválido ou expirado'}), 401

        id_usuario = data_token['id_usuario']
        usuario_info = Usuarios(db).get(id_usuario)

        if not usuario_info or usuario_info['tipo'] not in ['cooperativa', 'cooperado']:
            conn.close()
            return jsonify({'error': 'Acesso não autorizado'}), 403

        # 2. Buscar a avaliação pendente
        avaliacao = Avaliacoes(db).get_avaliacao_pendente_por_id(int(id_avaliacao_pendente))

        if not avaliacao:
            conn.close()
            return jsonify({'error': 'Avaliação não encontrada'}), 404

        conn.close()
        return jsonify(avaliacao), 200

    except Exception as e:
        if conn: conn.close()
        print(f"Erro em /avaliacao-pendente: {e}")
        return jsonify({'error': 'Erro interno no servidor'}), 500
