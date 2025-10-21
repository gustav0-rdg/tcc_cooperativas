from flask import Blueprint, request, jsonify
from controllers.usuarios_controller import Usuarios
from data.connection_controller import Connection
from controllers.tokens_controller import Tokens

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

        return jsonify({ 'error': 'Dados inválidos, todos os campos são obrigatórios' }), 400

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

        id_usuario = Usuarios(conn.connection_db).create(

            data_cadastro['nome'],
            data_cadastro['email'],
            data_cadastro['senha'],
            data_cadastro['tipo']

        )
        
        if id_usuario:

            return jsonify({ 

                'texto': 'Usuário cadastrado com sucesso!',
                'id_usuario': id_usuario

            }), 201
    
        else:

            return jsonify({ 'error': 'Erro ao cadastrar usuário'}), 500

    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()

@api_usuarios.route('/login', methods=['POST'])
def login ():

    data = request.get_json()

    email = data.get('email')
    senha = data.get('senha')

    if not email or not senha:

        return jsonify({ 'texto': '"email" e "senha" são parâmetros obrigatórios' }), 400

    try:

        conn = Connection('local')
        token_sessao = Usuarios(conn.connection_db).autenticar(email, senha)
        
        if token_sessao:

            return jsonify({ 'token': token_sessao }), 200
        
        else:

            return jsonify({ 'texto': 'Email ou Senha inválidos' }), 401
        
    finally:

        conn.close()
    
@api_usuarios.route('/alterar-senha', methods=['POST'])
def alterar_senha ():

    token = request.headers.get('Authorization')
    data = request.get_json()

    nova_senha = data.get('nova-senha')

    if not token or not nova_senha:

        return jsonify({ 'texto': '"token" e "nova-senha" são parâmetros obrigatórios' }), 400
    
    conn = Connection('local')

    try:

        token_controller = Tokens(conn.connection_db)
        data_token = token_controller.validar(token)

        if data_token and data_token['tipo'] == 'recuperacao_senha':

            if Usuarios(conn.connection_db).trocar_senha(data_token['id_usuario'], nova_senha) and token_controller.set_state(data_token['id_token']):

                return jsonify({ 'texto': 'Senha alterada com sucesso' }), 200
            
            else:

                return jsonify({ 'texto': 'Algo deu errado, tente novamente' }), 500

        else:

            return jsonify({ 'texto': 'Token inválido' }), 401

    finally:

        conn.close()

@api_usuarios.route('/delete', methods=['POST'])
@api_usuarios.route('/delete/<id_usuario>', methods=['POST'])
def delete (id_usuario:int=None):

    if id_usuario != None:

        if not id_usuario.isdigit():
            return jsonify({ 'error': '"id_usuario" deve ser um Int' }), 400

        id_usuario = int(id_usuario)

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400
    
    conn = Connection('local')

    try:

        data_token = Tokens(conn.connection_db).validar(token)

        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400

        #region Excluindo a conta de terceiros

        if data_token['id_usuario'] != id_usuario:

            if Usuarios(conn.connection_db).get_by_id(data_token['id_usuario'])['tipo'] == 'cooperativa':

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

    if id_usuario != None:

        if not id_usuario.isdigit():
            return jsonify({ 'error': '"id_usuario" deve ser um Int' }), 400

        id_usuario = int(id_usuario)

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400
    
    conn = Connection('local')

    try:

        data_token = Tokens(conn.connection_db).validar(token)
        if not data_token or data_token['tipo'] != 'sessao':

            return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400

        #region Consultando info de terceiros

        if data_token['id_usuario'] != id_usuario:

            if Usuarios(conn.connection_db).get_by_id(data_token['id_usuario'])['tipo'] == 'cooperativa':

                return jsonify({ 'error': 'Você não tem permissão para realizar tal ação' }), 403

        #endregion

        data_usuario = Usuarios(conn.connection_db).get_by_id(id_usuario)

        print(type(data_usuario))

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