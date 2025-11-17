from flask import Blueprint, request, redirect, jsonify
from controllers.comprador_controller import Compradores
from controllers.materiais_controller import Materiais
from controllers.feedback_controller import Feedbacks
from controllers.usuarios_controller import Usuarios
from controllers.tokens_controller import Tokens
from controllers.cooperativa_controller import Cooperativa
from controllers.comentarios_controller import Comentarios
from controllers.vendas_controller import Vendas
from controllers.precos_controller import Precos
from data.connection_controller import Connection
api_get = Blueprint('api_get', __name__, url_prefix='/get')

@api_get.route("/compradores", methods=["GET"])
def get_compradores():
    """
    Rota para buscar compradores com filtros opcionais.
    Query params:
        - material: ID do material base (opcional)
        - estado: Sigla do estado (opcional)
        - raio: Raio em km (opcional)
    """
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({ 'texto': '"token" é parâmetro obrigatório' }), 400

    conn = None
    try:
        conn = Connection('local')

        data_token = Tokens(conn.connection_db).validar(token)
        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({ 'error': '"Token" inexistente ou inválido'}), 401

        id_usuario = data_token['id_usuario']

        coop_info = Cooperativa(conn.connection_db).get_by_user_id(id_usuario)
        if not coop_info:
            return jsonify({ 'error': 'Cooperativa não encontrada' }), 404

        # Obter parâmetros de filtro da query string
        material_id = request.args.get('material', type=int)
        estado = request.args.get('estado', type=str)
        raio_km = request.args.get('raio', type=float)

        print(f"Filtros aplicados - Material: {material_id}, Estado: {estado}, Raio: {raio_km} km")

        # Buscar compradores com filtros
        compradores = Compradores(conn.connection_db).get_all(
            user_lat=coop_info['latitude'],
            user_lon=coop_info['longitude'],
            material_id=material_id,
            estado=estado,
            raio_km=raio_km
        )

        print(f"Total de compradores retornados: {len(compradores) if isinstance(compradores, list) else 0}")

        match compradores:
            # 404 - Compradores não encontrados
            case _ if isinstance(compradores, list) and len(compradores) <= 0:
                return jsonify({ 'error': 'Nenhum comprador encontrado com os filtros aplicados' }), 404
                
            # 200 - Compradores consultados
            case _ if isinstance(compradores, list) and len(compradores) > 0:
                return jsonify(compradores), 200

            # 500 - Erro ao consultar compradores
            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500

    except Exception as e:
        print(f"Erro ao buscar compradores: {e}")
        import traceback
        traceback.print_exc()
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
    Rota para obter a lista completa de materiais do catálogo com sinônimos da cooperativa.
    """
    conn = None
    try:
        conn = Connection('local')
        materiais = Materiais(conn.connection_db).get_all()

        # Obter id_cooperativa do token
        id_cooperativa = None
        token_header = request.headers.get('Authorization')
        if token_header:
            try:
                token = token_header.split(" ")[1]
                data_token = Tokens(conn.connection_db).validar(token)
                if data_token and data_token['tipo'] == 'sessao':
                    id_cooperativa = data_token['id_usuario']  # Assumindo que id_usuario é id_cooperativa
            except Exception as e:
                print(f"Erro ao validar token: {e}")

        # Adicionar sinônimos da cooperativa se token válido
        if id_cooperativa:
            cursor = conn.connection_db.cursor(dictionary=True)
            query_sinonimos = """
            SELECT msb.id_material_base, msb.nome_sinonimo
            FROM materiais_sinonimos_base msb
            WHERE msb.id_cooperativa = %s
            """
            cursor.execute(query_sinonimos, (id_cooperativa,))
            sinonimos = cursor.fetchall()
            cursor.close()

            # Criar dicionário de sinônimos por material base
            sinonimos_dict = {}
            for sin in sinonimos:
                if sin['id_material_base'] not in sinonimos_dict:
                    sinonimos_dict[sin['id_material_base']] = []
                sinonimos_dict[sin['id_material_base']].append(sin['nome_sinonimo'])

            # Adicionar sinônimos aos materiais
            for material in materiais:
                material['sinonimos'] = sinonimos_dict.get(material['id_material_base'], [])
        else:
            # Sem token, sinônimos vazios
            for material in materiais:
                material['sinonimos'] = []

        return jsonify(materiais), 200
    except Exception as e:
        print(f"Erro ao buscar materiais: {e}")
        import traceback
        traceback.print_exc()
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
    
@api_get.route("/compradores-destaque", methods=["GET"])
def get_compradores_destaque():
    token_header = request.headers.get('Authorization')
    if not token_header:
        return jsonify({'error': 'Token não fornecido'}), 401

    conn = Connection('local')
    try:
        # Validação do Token
        token = token_header.split(" ")[1]
        data_token = Tokens(conn.connection_db).validar(token)
        if not data_token or data_token['tipo'] != 'sessao':
            conn.close()
            return jsonify({'error': 'Token inválido ou expirado'}), 401

        # Obter filtros da query string
        material = request.args.get('material')
        estado = request.args.get('estado')
        score_min = request.args.get('score_min')

        compradores = Compradores(conn.connection_db).get_compradores_destaque(material_id=material, estado=estado, score_min=score_min)

        conn.close()
        return jsonify(compradores), 200

    except Exception as e:
        if conn: conn.close()
        print(f"Erro em /compradores-destaque: {e}")
        return jsonify({"erro": "Erro interno ao buscar compradores."}), 500

@api_get.route("/comprador-detalhes/<int:id_comprador>", methods=["GET"])
def get_comprador_detalhes(id_comprador):
    token_header = request.headers.get('Authorization')
    if not token_header:
        return jsonify({'error': 'Token não fornecido'}), 401

    conn = Connection('local')
    try:
        token = token_header.split(" ")[1]
        data_token = Tokens(conn.connection_db).validar(token)
        if not data_token or data_token['tipo'] != 'sessao':
            conn.close()
            return jsonify({'error': 'Token inválido ou expirado'}), 401

        detalhes = Compradores(conn.connection_db).get_detalhes_comprador(id_comprador)

        conn.close()
        return jsonify(detalhes), 200

    except Exception as e:
        if conn: conn.close()
        print(f"Erro em /comprador-detalhes: {e}")
        return jsonify({"erro": "Erro interno ao buscar detalhes do comprador."}), 500

@api_get.route("/precos-mercado", methods=["GET"])
def get_precos_mercado():
    """
    Rota para obter preços de mercado anonimizados.
    Parâmetros opcionais: estado, ano, mes
    """
    try:
        conn = Connection('local')
        estado = request.args.get('estado')
        ano = request.args.get('ano')
        mes = request.args.get('mes')

        precos = Precos(conn.connection_db).get_precos_mercado_anonimizado(estado, ano, mes)
        return jsonify(precos), 200
    except Exception as e:
        print(f"Erro ao buscar preços de mercado: {e}")
        return jsonify({"erro": "Ocorreu um erro interno no servidor"}), 500
    finally:
        if conn:
            conn.close()

@api_get.route("/precos-regionais", methods=["GET"])
def get_precos_regionais():
    """
    Rota para obter preços regionais.
    Parâmetros opcionais: material_id, estado
    """
    try:
        conn = Connection('local')
        material_id = request.args.get('material_id')
        estado = request.args.get('estado')

        precos = Precos(conn.connection_db).get_precos_regionais(material_id, estado)
        return jsonify(precos), 200
    except Exception as e:
        print(f"Erro ao buscar preços regionais: {e}")
        return jsonify({"erro": "Ocorreu um erro interno no servidor"}), 500
    finally:
        if conn:
            conn.close()

@api_get.route("/compradores-avaliacoes-count", methods=["GET"])
def get_compradores_avaliacoes_count():
    """
    Rota para obter a contagem de avaliações por comprador.
    """
    try:
        conn = Connection('local')
        cursor = conn.connection_db.cursor(dictionary=True)
        query = """
        SELECT c.razao_social, COUNT(ac.id_avaliacao) as total_avaliacoes
        FROM compradores c
        LEFT JOIN vendas v ON c.id_comprador = v.id_comprador
        LEFT JOIN avaliacoes_compradores ac ON v.id_venda = ac.id_venda
        GROUP BY c.id_comprador, c.razao_social
        ORDER BY total_avaliacoes DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        return jsonify(results), 200
    except Exception as e:
        print(f"Erro ao buscar contagem de avaliações por comprador: {e}")
        return jsonify({"erro": "Ocorreu um erro interno no servidor"}), 500
    finally:
        if conn:
            conn.close()

@api_get.route("/cooperativa-info", methods=["GET"])
def get_cooperativa_info():
    token_header = request.headers.get('Authorization')
    if not token_header:
        return jsonify({'error': 'Token não fornecido'}), 401

    try:
        token = token_header.split(" ")[1]
    except IndexError:
        return jsonify({'error': 'Token mal formatado'}), 401

    conn = Connection('local')
    try:
        data_token = Tokens(conn.connection_db).validar(token)
        if not data_token or data_token['tipo'] != 'sessao':
            conn.close()
            return jsonify({'error': 'Token inválido ou expirado'}), 401

        id_usuario = data_token['id_usuario']
        cooperativa = Cooperativa(conn.connection_db).get_cooperativa_by_user_id(id_usuario)

        if not cooperativa:
            conn.close()
            return jsonify({'error': 'Cooperativa não encontrada'}), 404

        # Parse endereco into rua and bairro
        endereco_parts = cooperativa['endereco'].split(',') if cooperativa['endereco'] else ['', '']
        rua = endereco_parts[0].strip() if len(endereco_parts) > 0 else ''
        bairro = endereco_parts[1].strip() if len(endereco_parts) > 1 else ''
        cidade_estado = f"{cooperativa['cidade']} - {cooperativa['estado']}" if cooperativa['cidade'] and cooperativa['estado'] else ''

        response = {
            'nome_fantasia': cooperativa['nome_fantasia'],
            'cnpj': cooperativa['cnpj'],
            'rua': rua,
            'bairro': bairro,
            'cidade_estado': cidade_estado,
            'telefone_fixo': cooperativa['telefone'],
            'email': cooperativa['email'],
            'whatsapp': None,  # Campo não presente na tabela cooperativas
            'site': None  # Campo não presente na tabela cooperativas
        }

        conn.close()
        return jsonify(response), 200

    except Exception as e:
        if conn:
            conn.close()
        print(f"Erro em /get/cooperativa-info: {e}")
        return jsonify({'error': 'Erro interno no servidor'}), 500
