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

    if not data_cadastro or not all(key in data_cadastro for key in ['nome', 'email', 'senha']):
        
        return jsonify({ 'error': 'Dados de cadastro inválidos, todos os campos são obrigatórios: nome, email e senha' }), 400

    if len(data_cadastro['senha']) < 8:
        return jsonify({ 'texto': 'A senha deve ter no minímo 8 caractéres' }), 400

    if not 'tipo' in data_cadastro:
        data_cadastro['tipo'] = 'cooperativa'

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
def login ():

    data = request.get_json()

    email = data.get('email')
    if not email:
        return jsonify({ 'texto': '"email" é parâmetro obrigatório' }), 400
        
    senha = data.get('senha')
    if not senha:
        return jsonify({ 'texto': '"senha" é parâmetro obrigatório' }), 400
    
    conn = Connection('local')

    try:

        autenticar_usuario = Usuarios(conn.connection_db).autenticar(email, senha)
        match autenticar_usuario:

            # 404 - Usuário não encontrado (Email ou Senha incorretos)

            case None:
                return jsonify({ 'error': 'Email ou senha incorretos' }), 404

            # 200 - Usuário autêntico

            case _ if isinstance(autenticar_usuario, int):

                return jsonify({ 
                    
                    'token': Tokens(conn.connection_db).create(

                        autenticar_usuario,
                        'sessao',

                        # Data de expiração em 30 dias
                        datetime.now() + timedelta(days=30)

                    )

                }), 200

            # 500 - Erro ao verificar a autenticidade do usuário

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500

    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()
    
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