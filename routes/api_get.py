from flask import Blueprint, request, redirect, jsonify
from controllers.comprador_controller import Compradores
from controllers.materiais_controller import Materiais
from controllers.feedback_controller import Feedbacks
from controllers.usuarios_controller import Usuarios
from controllers.tokens_controller import Tokens
from controllers.cooperativa_controller import Cooperativa
from controllers.cooperados_controller import Catadores
from controllers.comentarios_controller import Comentarios
from controllers.vendas_controller import Vendas
from controllers.avaliacoes_controller import Avaliacoes
from data.connection_controller import Connection
api_get = Blueprint('api_get', __name__, url_prefix='/get')

@api_get.route("/compradores", methods=["GET"])
def get_compradores():
    """
    Rota para buscar compradores com filtros opcionais.
    Acessível por 'cooperativa' e 'cooperado'.
    Query params:
        - material: ID do material base (opcional)
        - estado: Sigla do estado (opcional)
        - raio: Raio em km (opcional)
    """
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'texto': '"token" é parâmetro obrigatório'}), 400

    conn = None
    try:
        conn = Connection()
        db = conn.connection_db

        data_token = Tokens(db).validar(token)
        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({'error': 'Token inexistente ou inválido'}), 401

        id_usuario = data_token['id_usuario']
        usuario_info = Usuarios(db).get(id_usuario)

        if not usuario_info:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        user_type = usuario_info.get('tipo')
        coop_info = None

        if user_type == 'cooperativa':
            coop_info = Cooperativa(db).get_by_user_id(id_usuario)
        elif user_type == 'cooperado':
            catador_info = Catadores(db).get_by_id_usuario(id_usuario)
            if catador_info and 'id_cooperativa' in catador_info:
                id_cooperativa = catador_info['id_cooperativa']
                coop_info = Cooperativa(db).get_by_id(id_cooperativa)
            else:
                return jsonify({'error': 'Cooperado não está vinculado a uma cooperativa'}), 404
        else:
            return jsonify({'error': 'Acesso não autorizado para este tipo de usuário'}), 403

        if not coop_info:
            return jsonify({'error': 'Informações da cooperativa não encontradas'}), 404

        # Obter parâmetros de filtro da query string
        material_id = request.args.get('material', type=int)
        estado = request.args.get('estado', type=str)
        raio_km = request.args.get('raio', type=float)

        print(f"Filtros aplicados - Material: {material_id}, Estado: {estado}, Raio: {raio_km} km")

        # Buscar compradores com filtros
        compradores = Compradores(db).get_all(
            user_lat=coop_info['latitude'],
            user_lon=coop_info['longitude'],
            material_id=material_id,
            estado=estado,
            raio_km=raio_km
        )

        print(f"Total de compradores retornados: {len(compradores) if isinstance(compradores, list) else 0}")

        match compradores:
            case _ if isinstance(compradores, list) and len(compradores) <= 0:
                return jsonify([]), 200
            case _ if isinstance(compradores, list) and len(compradores) > 0:
                return jsonify(compradores), 200
            case False | _:
                return jsonify({'error': 'Ocorreu um erro ao consultar compradores'}), 500

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
    Rota para obter a lista de materiais.
    Se um token de autenticação for fornecido, a lista pode incluir sinônimos.
    """
    conn = None
    try:
        conn = Connection('local')
        db = conn.connection_db
        id_cooperativa = None

        token_header = request.headers.get('Authorization')
        if token_header:
            try:
                token = token_header.split(" ")[1] if " " in token_header else token_header
                data_token = Tokens(db).validar(token)

                if data_token:
                    id_usuario = data_token['id_usuario']
                    usuario_info = Usuarios(db).get(id_usuario)

                    if usuario_info:
                        if usuario_info['tipo'] == 'cooperativa':
                            coop_info = Cooperativa(db).get_by_user_id(id_usuario)
                            if coop_info:
                                id_cooperativa = coop_info.get('id_cooperativa')
                        elif usuario_info['tipo'] == 'cooperado':
                            catador_info = Catadores(db).get_by_id_usuario(id_usuario)
                            if catador_info:
                                id_cooperativa = catador_info.get('id_cooperativa')
            except Exception as e:
                print(f"Erro ao processar token em /materiais: {e}")
                # Continua sem id_cooperativa, não retorna erro

        materiais = Materiais(db).get_all(id_cooperativa=id_cooperativa)
        return jsonify(materiais), 200

    except Exception as e:
        print(f"Erro ao buscar materiais: {e}")
        return jsonify({"error": "Ocorreu um erro interno no servidor"}), 500
    finally:
        if conn:
            conn.close()

@api_get.route("/subtipos/<int:material_id>", methods=["GET"])
def get_subtipos_materiais(material_id):
    """
    Rota para obter a lista de subtipos de um material.
    Se um token for fornecido, pode retornar nomes de sinônimos.
    """
    conn = None
    try:
        conn = Connection('local')
        db = conn.connection_db
        id_cooperativa = None

        token_header = request.headers.get('Authorization')
        if token_header:
            try:
                token = token_header.split(" ")[1] if " " in token_header else token_header
                data_token = Tokens(db).validar(token)

                if data_token:
                    id_usuario = data_token['id_usuario']
                    usuario_info = Usuarios(db).get(id_usuario)

                    if usuario_info:
                        if usuario_info['tipo'] == 'cooperativa':
                            coop_info = Cooperativa(db).get_by_user_id(id_usuario)
                            if coop_info:
                                id_cooperativa = coop_info.get('id_cooperativa')
                        elif usuario_info['tipo'] == 'cooperado':
                            catador_info = Catadores(db).get_by_id_usuario(id_usuario)
                            if catador_info:
                                id_cooperativa = catador_info.get('id_cooperativa')
            except Exception as e:
                print(f"Erro ao processar token em /subtipos: {e}")

        materiais = Materiais(db).get_subtipos(material_id, id_cooperativa=id_cooperativa)
        return jsonify(materiais), 200

    except Exception as e:
        print(f"Erro ao buscar subtipos de materiais: {e}")
        return jsonify({"error": "Ocorreu um erro interno no servidor"}), 500
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

    conn = Connection('local')

    try:
        # 1. Validar o Token e Permissão (reaproveitando a lógica de segurança)
        db = conn.connection_db
        # Remove o prefixo "Bearer " se ele existir
        token = token_header.split(" ")[1] if " " in token_header else token_header
        data_token = Tokens(db).validar(token)
        if data_token is None:
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
        if data_token is None:
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

@api_get.route('/comprador-detalhes/<int:id_comprador>', methods=['GET'])
def get_comprador_detalhes(id_comprador):
    """
    Rota para obter os detalhes de um comprador específico.
    """
    token_header = request.headers.get('Authorization')
    if not token_header:
        return jsonify({'error': 'Token não fornecido'}), 401

    conn = Connection('local')

    try:
        # 1. Validar o Token e Permissão
        db = conn.connection_db
        token = token_header.split(" ")[1] if " " in token_header else token_header
        data_token = Tokens(db).validar(token)
        if data_token is None:
            conn.close()
            return jsonify({'error': 'Token inválido ou expirado'}), 401

        id_usuario = data_token['id_usuario']
        usuario_info = Usuarios(db).get(id_usuario)

        if not usuario_info or usuario_info['tipo'] not in ['cooperativa', 'cooperado', 'gestor', 'root']:
            conn.close()
            return jsonify({'error': 'Acesso não autorizado'}), 403

        # 2. Buscar os detalhes do comprador
        detalhes = Compradores(db).get_detalhes_comprador(id_comprador)

        if not detalhes:
            conn.close()
            return jsonify({'error': 'Detalhes do comprador não encontrados'}), 404

        conn.close()
        return jsonify(detalhes), 200

    except Exception as e:
        if conn: conn.close()
        print(f"Erro em /comprador-detalhes: {e}")
        return jsonify({'error': 'Erro interno no servidor'}), 500

@api_get.route('/cooperativa-info', methods=['GET'])
def get_cooperativa_info():
    """
    Retorna as informações detalhadas da cooperativa logada.
    """
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Token é obrigatório'}), 401

    conn = None
    try:
        conn = Connection('local')
        db = conn.connection_db

        # Validar token
        data_token = Tokens(db).validar(token)
        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({'error': 'Token inválido ou expirado'}), 401

        id_usuario = data_token['id_usuario']
        
        # Verificar se o usuário é uma cooperativa
        usuario_info = Usuarios(db).get(id_usuario)
        if not usuario_info or usuario_info['tipo'] != 'cooperativa':
            return jsonify({'error': 'Usuário não é uma cooperativa'}), 403

        # Buscar dados da cooperativa usando o método já corrigido
        dados_cooperativa = Cooperativa(db).get_by_user_id(id_usuario)
        if not dados_cooperativa:
            return jsonify({'error': 'Dados da cooperativa não encontrados'}), 404

        return jsonify(dados_cooperativa), 200

    except Exception as e:
        print(f"Erro em /get/cooperativa-info: {e}")
        return jsonify({'error': 'Erro interno no servidor'}), 500
    finally:
        if conn:
            conn.close()
