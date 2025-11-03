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
def cadastrar ():

    token = request.headers.get('Authorization')

    data_cadastro = request.get_json()
    campos_obrigatorios =  ['nome', 'email', 'senha', 'tipo']

    # 400 - Campos obrigatórios incompletos

    if not data_cadastro or not all(key in data_cadastro for key in campos_obrigatorios):
        return jsonify({ 'error': 'Dados de cadastro inválidos, todos os campos são obrigatórios: nome, email e senha' }), 400

    # 400 - Senha com menos de 8 caractéres

    if len(data_cadastro['senha']) < 8:
        return jsonify({ 'texto': 'A senha deve ter no minímo 8 caractéres' }), 400
    
    conn = Connection('local')

    try:

        #region Cadastro de pessoas com permissões especiais

        if data_cadastro['tipo'] != 'cooperativa':

            if not token:
                return jsonify({ 'error': 'Para este tipo de ação é necessário token de autorização' }), 400
            
            data_token = Tokens(conn.connection_db).validar(token)
            usuario = Usuarios(conn.connection_db).get_by_id(data_token['id_usuario'])

            if data_cadastro['tipo'] == 'root' or usuario['tipo'] != 'root':
                return jsonify({ 'error': 'Você não tem permissão para realizar tal ação' }), 403
            
        #endregion

        novo_usuario = Usuarios(conn.connection_db).create(

            data_cadastro['nome'],

            data_cadastro['email'],
            data_cadastro['senha'],

            data_cadastro['tipo']

        )

        match novo_usuario:

            # 200 - Usuário criado

            case _ if isinstance(novo_usuario, int):

                return jsonify({ 

                    'texto': 'Usuário cadastrado',
                    'id_usuario': novo_usuario

                }), 200

            # 500 - Erro ao criar usuário

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500

    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()

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
                return jsonify(data_usuario), 200

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