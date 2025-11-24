from flask import redirect, Blueprint, request, jsonify
from controllers.comprador_controller import Compradores
from controllers.vendas_controller import Vendas
from data.connection_controller import Connection
from controllers.materiais_controller import Materiais
from controllers.cooperados_controller import Catadores
from controllers.tokens_controller import Tokens
from controllers.avaliacoes_controller import Avaliacoes
from controllers.cooperativa_controller import Cooperativa
from controllers.usuarios_controller import Usuarios

api_post = Blueprint('api_post', __name__, url_prefix="/post")

@api_post.route("/dados-venda", methods=["POST"])
def postar_dados_de_venda():
    conn = None
    try:
        dados_recebidos = request.get_json()
        conn = Connection('local')
        
        sucesso = Vendas(conn.connection_db).registrar_nova_venda(
            dados_recebidos["id_cooperativa"], 
            dados_recebidos
        )
        
        if sucesso:
            return jsonify({"status": "sucesso", "mensagem": "Dados da venda recebidos e processados!"}), 200
        else:
            return jsonify({"erro": "Falha ao registrar a venda"}), 500
            
    except Exception as e:
        # Adiciona log do erro para facilitar a depuração
        print(f"Erro na rota /dados-venda: {e}")
        return jsonify({"erro": "Ocorreu um erro interno no servidor"}), 500
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
        return jsonify({"erro": "Ocorreu um erro interno no servidor"}), 500
    finally:
        conn.close()

# Corrigido: Agora obtém id_cooperativa corretamente do token

@api_post.route("/cadastrar-sinonimo", methods=["POST"])
def registrar_sinonimo():
    conn = None
    try:
        data = request.get_json()
        nome_padrao = data.get('nome_padrao')
        sinonimo = data.get('sinonimo')

        token_header = request.headers.get('Authorization')
        if not token_header:
            return jsonify({'error': 'Token não fornecido'}), 401

        try:
            token = token_header.split(" ")[1] if " " in token_header else token_header
        except IndexError:
            return jsonify({'error': 'Token mal formatado'}), 401

        conn = Connection('local')
        db = conn.connection_db
        data_token = Tokens(db).validar(token)
        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({'error': 'Token inválido ou expirado'}), 401

        id_usuario = data_token['id_usuario']
        
        # Corrigido: Buscar id_cooperativa a partir do id_usuario
        coop_info = Cooperativa(db).get_by_user_id(id_usuario)
        if not coop_info or 'id_cooperativa' not in coop_info:
            return jsonify({'error': 'Cooperativa não encontrada para este usuário'}), 404
            
        id_cooperativa = coop_info['id_cooperativa']

        if not all([nome_padrao, sinonimo]):
            return jsonify({'message': 'Faltam dados para registrar o sinônimo.'}), 400

        resposta = Materiais(db).post_cadastrar_sinonimo(nome_padrao, sinonimo, id_cooperativa)
        return resposta
    except Exception as e:
        # Log do erro para depuração
        print(f"Erro em /post/cadastrar-sinonimo: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500
    finally:
        if conn:
            conn.close()

@api_post.route("/cadastrar-material-base", methods=["POST"])
def cadastrar_material_base():
    try:
        data = request.get_json()
        nome_material = data.get('nome_material')
        id_cooperativa = 1  # TODO: Obter do token

        if not nome_material:
            return jsonify({'message': 'Nome do material é obrigatório.'}), 400

        # Obter id_cooperativa do token
        token_header = request.headers.get('Authorization')
        if not token_header:
            return jsonify({'error': 'Token não fornecido'}), 401

        try:
            token = token_header.split(" ")[1] if " " in token_header else token_header
        except IndexError:
            return jsonify({'error': 'Token mal formatado'}), 401

        conn = Connection('local')
        data_token = Tokens(conn.connection_db).validar(token)
        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({'error': 'Token inválido ou expirado'}), 401

        # Obter id_cooperativa do usuário logado
        from controllers.cooperativa_controller import Cooperativa
        coop_info = Cooperativa(conn.connection_db).get_by_user_id(data_token['id_usuario'])
        if not coop_info:
            return jsonify({'error': 'Cooperativa não encontrada para o usuário'}), 404
        id_cooperativa = coop_info['id_cooperativa']

        resposta = Materiais(conn.connection_db).cadastrar_material_base(nome_material, id_cooperativa)
        return resposta
    except Exception as e:
        print(e)
    finally:
        if conn:
            conn.close()

@api_post.route("/cadastrar-subtipo", methods=["POST"])
def cadastrar_subtipo():
    try:
        data = request.get_json()
        conn = Connection('local')
        resposta = Materiais(conn.connection_db).cadastrar_subtipo(data["nome_especifico"], data["id_material_base"])
        return jsonify({'sucesso':'cadastro'})
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500
    finally:
        conn.close()

@api_post.route("/cadastrar-sinonimo-base", methods=["POST"])
def cadastrar_sinonimo_base():
    try:
        data = request.get_json()
        id_material_base = data.get('id_material_base')
        sinonimo = data.get('sinonimo')

        if not all([id_material_base, sinonimo]):
            return jsonify({'message': 'Dados incompletos.'}), 400

        # Obter id_cooperativa do token
        token_header = request.headers.get('Authorization')
        if not token_header:
            return jsonify({'error': 'Token não fornecido'}), 401

        try:
            token = token_header.split(" ")[1]
        except IndexError:
            return jsonify({'error': 'Token mal formatado'}), 401

        conn = Connection('local')
        data_token = Tokens(conn.connection_db).validar(token)
        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({'error': 'Token inválido ou expirado'}), 401

        # Obter id_cooperativa do usuário logado
        from controllers.cooperativa_controller import Cooperativa
        coop_info = Cooperativa(conn.connection_db).get_by_user_id(data_token['id_usuario'])
        if not coop_info:
            return jsonify({'error': 'Cooperativa não encontrada para o usuário'}), 404
        id_cooperativa = coop_info['id_cooperativa']

        resposta = Materiais(conn.connection_db).post_cadastrar_sinonimo_base(id_material_base, sinonimo, id_cooperativa)
        return resposta

    except Exception as e:
        return jsonify({'message': 'Erro interno do servidor.'}), 500
    finally:
        if 'conn' in locals():
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
        return jsonify({'error': 'Erro interno no servidor'}), 500

@api_post.route('/salvar-informacoes', methods=['POST'])
def salvar_informacoes():
    """
    Rota para salvar as informações atualizadas da cooperativa.
    """
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Token é obrigatório'}), 401

    dados = request.get_json()
    if not dados:
        return jsonify({'error': 'Dados não fornecidos'}), 400

    conn = None
    try:
        conn = Connection('local')
        db = conn.connection_db

        # Validar token
        data_token = Tokens(db).validar(token)
        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({'error': 'Token inválido ou expirado'}), 401

        id_usuario = data_token['id_usuario']
        
        # Obter o id_cooperativa a partir do id_usuario
        coop_info = Cooperativa(db).get_by_user_id(id_usuario)
        if not coop_info or 'id_cooperativa' not in coop_info:
            return jsonify({'error': 'Cooperativa não encontrada'}), 404
        
        id_cooperativa = coop_info['id_cooperativa']

        # Chamar o controller para atualizar os dados
        sucesso = Cooperativa(db).update_info(id_cooperativa, dados)

        if sucesso:
            return jsonify({'status': 'sucesso', 'mensagem': 'Informações salvas com sucesso!'}), 200
        else:
            return jsonify({'error': 'Nenhuma informação foi alterada ou ocorreu um erro'}), 400

    except Exception as e:
        print(f"Erro em /post/salvar-informacoes: {e}")
        return jsonify({'error': 'Erro interno no servidor'}), 500
    finally:
        if conn:
            conn.close()