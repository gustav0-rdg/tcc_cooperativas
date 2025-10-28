from flask import Blueprint, request, jsonify
from controllers.usuarios_controller import Usuarios
from data.connection_controller import Connection
from controllers.tokens_controller import Tokens
from datetime import datetime, timedelta

api_usuarios = Blueprint(
    
    'api_usuarios', 
    __name__, 

    url_prefix='/api/usuarios'
    
)

@api_usuarios.route('/cadastrar', methods=['POST'])
def cadastrar():

    conn = None
    try:
        data_cadastro = request.get_json()
        
        # Campos base obrigatórios
        nome = data_cadastro.get('nome')
        senha = data_cadastro.get('senha')
        tipo_novo_usuario = data_cadastro.get('tipo')
        
        email = data_cadastro.get('email') 
        cpf = data_cadastro.get('cpf') # Para cooperados

        #region Validações básicas
        if not nome or not senha or not tipo_novo_usuario:
            return jsonify({'error': 'Nome, senha e tipo são obrigatórios'}), 400
        if len(senha) < 8:
            return jsonify({'error': 'A senha deve ter no mínimo 8 caracteres'}), 400
        #endregion

        conn = Connection('local')
        if not conn.connection_db or not conn.connection_db.is_connected():
             raise ConnectionError("Falha ao conectar ao banco de dados")

        status_inicial = 'pendente'

        if tipo_novo_usuario != 'cooperativa':
            token_header = request.headers.get('Authorization')
            if not token_header or not token_header.startswith("Bearer "):
                 conn.close(); return jsonify({'error': 'Token de autorização ausente ou mal formatado'}), 401
            token = token_header.split(" ")[1]
            
            tokens_ctrl = Tokens(conn.connection_db)
            data_token = tokens_ctrl.validar(token)
            if not data_token: conn.close(); return jsonify({'error': 'Token inválido'}), 401
            
            id_usuario_logado = data_token['id_usuario']
            token_valido_agora = tokens_ctrl.get_ultimo_token_por_usuario(id_usuario_logado, 'sessao')
            if not token_valido_agora or token_valido_agora != token: conn.close(); return jsonify({'error': 'Token expirado ou inválido'}), 401

            usuarios_ctrl_check = Usuarios(conn.connection_db)
            usuario_logado = usuarios_ctrl_check.get_by_id(id_usuario_logado)
            if not usuario_logado: conn.close(); return jsonify({'error': 'Usuário requisitante não encontrado'}), 404
            
            if usuario_logado['tipo'] != 'root':
                conn.close(); return jsonify({'error': 'Apenas o usuário Root pode criar este tipo de conta'}), 403
            
            if tipo_novo_usuario == 'root':
                 conn.close(); return jsonify({'error': 'Não é permitido criar outro usuário Root'}), 403

            if tipo_novo_usuario == 'gestor' or tipo_novo_usuario == 'cooperado':
                status_inicial = 'ativo'
            
            # Validação de dados específicos do tipo
            if tipo_novo_usuario == 'gestor' and not email:
                 conn.close(); return jsonify({'error': 'Email é obrigatório para criar um gestor'}), 400
            if tipo_novo_usuario == 'cooperado' and not cpf:
                 conn.close(); return jsonify({'error': 'CPF é obrigatório para criar um cooperado'}), 400
                 
        else:
             if not email:
                  conn.close(); return jsonify({'error': 'Email é obrigatório para cadastro de cooperativa'}), 400

        usuarios_ctrl_create = Usuarios(conn.connection_db)
        
        id_criado, msg_status = usuarios_ctrl_create.create(
            nome=nome,
            senha=senha,
            tipo=tipo_novo_usuario,
            email=email, 
            cpf=cpf,     
            status=status_inicial 
        )
        
        conn.close()

        if id_criado is not None:
            return jsonify({'id_usuario': id_criado, 'message': f'Usuário {tipo_novo_usuario} base criado com sucesso!'}), 201
        else:
            return jsonify({'error': msg_status or f'Erro ao criar {tipo_novo_usuario}.'}), 409 # Ou 500

    except ConnectionError as ce:
         print(f"Erro de Conexão na rota /cadastrar: {ce}")
         return jsonify({'error': 'Falha na conexão com o banco de dados'}), 500
         
    except Exception as e:
        if conn and conn.connection_db and conn.connection_db.is_connected(): conn.close()
        print(f"Erro GERAL Inesperado na rota /cadastrar: {e}")
        return jsonify({'error': 'Erro interno inesperado no servidor'}), 50

@api_usuarios.route('/login', methods=['POST'])
def login_generico():

    conn = None

    try:
        data = request.get_json()
        identificador = data.get('identificador')
        senha = data.get('senha')

        if not identificador or not senha:
            return jsonify({'error': 'Identificador e senha são obrigatórios'}), 400
        
        conn = Connection('local')
        usuario_controller = Usuarios(conn.connection_db)
        
        token, status_msg = usuario_controller.autenticar(identificador, senha)
        
        conn.close() 

        if status_msg == "LOGIN_SUCESSO" and token:
            # Envia o token para o JavaScript
            return jsonify({'token': token}), 200
        else:
            # Falha na autenticação, traduz a mensagem
            erros = {
                "IDENTIFICADOR_NAO_ENCONTRADO": "Usuário não encontrado.",
                "SENHA_INVALIDA": "Senha inválida.",
                "USUARIO_PENDENTE": "Cadastro pendente de aprovação.",
                "USUARIO_INATIVO": "Este usuário está inativo.",
                "USUARIO_BLOQUEADO": "Este usuário foi bloqueado.",
                "COOPERATIVA_NAO_APROVADA": "Cadastro da cooperativa ainda não foi aprovado.",
                "COOPERADO_INATIVO": "Este cooperado está inativo.",
            }

            mensagem_erro = erros.get(status_msg, "Credenciais inválidas ou usuário não autorizado")
            return jsonify({'error': mensagem_erro}), 401

    except Exception as e:
        if conn: conn.close()
        print(f"Erro na rota /login: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@api_usuarios.route('/alterar-senha', methods=['POST'])
def alterar_senha ():

    token = request.headers.get('Authorization')

    if not token:
        return jsonify({ 'texto': '"token" é parâmetro obrigatório' }), 400

    data = request.get_json()
    nova_senha = data.get('nova-senha')

    if not nova_senha:
        return jsonify({ 'texto': '"nova-senha" é parâmetro obrigatório' }), 400
    
    if len(nova_senha) < 8:
        return jsonify({ 'texto': 'A senha deve ter no minímo 8 caractéres' }), 400
    
    conn = Connection('local')

    try:

        data_token = Tokens(conn.connection_db).validar(token)

        if not data_token or data_token['tipo'] != 'recuperacao_senha':
            return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400

        match Usuarios(conn.connection_db).trocar_senha(data_token['id_usuario']):

            # 404 - Usuário não encontrado

            case None:
                return jsonify({ 'error': 'Usuário não encontrado' }), 404

            # 200 - Senha do usuário alterada

            case True:

                Tokens(conn.connection_db).set_state(data_token['id_token'])
                return jsonify({ 'texto': 'Senha alterada com sucesso' }), 200

            # 500 - Erro ao alterar a senha do usuário

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500

    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()

@api_usuarios.route('/delete', methods=['POST'])
@api_usuarios.route('/delete/<id_usuario>', methods=['POST'])
def delete (id_usuario:int=None):

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400
    
    conn = Connection('local')

    try:

        data_token = Tokens(conn.connection_db).validar(token)

        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400

        if id_usuario != None:

            if not id_usuario.isdigit():
                return jsonify({ 'error': '"id_usuario" deve ser um Int' }), 400

            id_usuario = int(id_usuario)

        else:

            id_usuario = data_token['id_usuario']

        #region Excluindo a conta de terceiros

        if data_token['id_usuario'] != id_usuario and Usuarios(conn.connection_db).get_by_id(data_token['id_usuario'])['tipo'] == 'cooperativa':

            return jsonify({ 'error': 'Você não tem permissão para realizar tal ação' }), 403
            
        #endregion
        
        match Usuarios(conn.connection_db).delete(id_usuario):

            # 404 - Usuário não encontrado

            case None:
                return jsonify({ 'error': 'Usuário não encontrado' }), 404

            # 200 - Usuário Excluído

            case True:
                return jsonify({ 'texto': 'Usuário excluído' }), 200

            # 500 - Erro ao excluir usuário

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500
    
    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()

@api_usuarios.route('/get', methods=['POST'])
@api_usuarios.route('/get/<id_usuario>', methods=['POST'])
def get_info (id_usuario:int=None):

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400
    
    conn = Connection('local')

    try:

        data_token = Tokens(conn.connection_db).validar(token)
        
        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400
        
        if id_usuario != None:

            if not id_usuario.isdigit():
                return jsonify({ 'error': '"id_usuario" deve ser um Int' }), 400

            id_usuario = int(id_usuario)

        else:

            id_usuario = data_token['id_usuario']

        #region Consultando info de terceiros

        if data_token['id_usuario'] != id_usuario and Usuarios(conn.connection_db).get_by_id(data_token['id_usuario'])['tipo'] == 'cooperativa':

            return jsonify({ 'error': 'Você não tem permissão para realizar tal ação' }), 403

        #endregion

        data_usuario = Usuarios(conn.connection_db).get_by_id(id_usuario)
        match data_usuario:

            # 404 - Usuário não encontrado

            case None:
                return jsonify({ 'error': 'Usuário não encontrado' }), 404

            # 200 - Informações do usuário consultadas

            case _ if isinstance(data_usuario, dict):
                return jsonify({ 'data': data_usuario }), 200

            # 500 - Erro ao consultar as informações usuário

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500
    
    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()

@api_usuarios.route('/alterar-status', methods=['POST'])
@api_usuarios.route('/alterar-status/<id_usuario>', methods=['POST'])
def alterar_status (id_usuario:int=None):

    data = request.get_json()

    novo_status = data.get('novo-status')
    if not novo_status:
        return jsonify({ 'error': '"novo-status" é um parâmetro obrigatório' }), 400

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400
    
    conn = Connection('local')

    try:

        data_token = Tokens(conn.connection_db).validar(token)
        if not data_token:
            return jsonify({ 'error': 'Token inválido' }), 400

        if id_usuario != None:

            if not id_usuario.isdigit():
                return jsonify({ 'error': '"id_usuario" deve ser um Int' }), 400

            id_usuario = int(id_usuario)

        else:

            id_usuario = data_token['id_usuario']

        match novo_status:

            case 'ativo':

                if not (data_token['tipo'] == 'cadastro' or (data_token['tipo'] == 'sessao' and Usuarios(conn.connection_db).get_by_id(data_token['id_usuario'])['tipo'] != 'cooperativa')):

                    return jsonify({ 'error': 'Você não tem permissão para tal ação' }), 403
                
            case 'inativo' | 'bloqueado':

                if not (data_token['tipo'] == 'sessao' and Usuarios(conn.connection_db).get_by_id(data_token['id_usuario'])['tipo'] != 'cooperativa'):

                    return jsonify({ 'error': 'Você não tem permissão para tal ação' }), 403

            case _:

                return jsonify({ 'error': '"novo-status" inválido' }), 400

        #region Alterando o status de terceiros

        if data_token['id_usuario'] != id_usuario and not Usuarios(conn.connection_db).get_by_id(data_token['id_usuario'])['tipo'] != 'cooperativa':

            return jsonify({ 'error': 'Você não tem permissão para realizar tal ação' }), 403

        #endregion

        match Usuarios(conn.connection_db).alterar_status(id_usuario, novo_status):

            # 404 - Usuário não encontrado

            case None:
                return jsonify({ 'error': 'Usuário não encontrado' }), 404

            # 200 - Status do usuário alterado

            case True:
                return jsonify({ 'texto': 'Status do usuário alterado' }), 200

            # 500 - Erro ao alterar o status

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500
    
    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()
        


@api_usuarios.route('/me', methods=['GET'])
def get_meu_usuario():

    conn = None
    try:

        token_header = request.headers.get('Authorization')
        
        if not token_header:
            return jsonify({'error': 'Token não fornecido'}), 401
        
        try:
            token = token_header.split(" ")[1]
        except IndexError:
            return jsonify({'error': 'Token mal formatado'}), 401

        conn = Connection('local')
        db = conn.connection_db
        tokens_ctrl = Tokens(db)

        data_token = tokens_ctrl.validar(token)

        if not data_token:
            return jsonify({'error': 'Token inválido'}), 401
        
        id_usuario = data_token['id_usuario']
        token_valido_agora = tokens_ctrl.get_ultimo_token_por_usuario(id_usuario, 'sessao')

        if not token_valido_agora or token_valido_agora != token:
             return jsonify({'error': 'Token expirado ou inválido'}), 401

        usuarios_ctrl = Usuarios(db)
        usuario_info = usuarios_ctrl.get_by_id(id_usuario)

        conn.close()

        if not usuario_info:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        return jsonify({
            'id_usuario': usuario_info['id_usuario'],
            'nome': usuario_info['nome'],
            'email': usuario_info['email'],
            'tipo': usuario_info['tipo']
        }), 200

    except Exception as e:
        if conn: conn.close()
        print(f"Erro GERAL na rota /me: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500