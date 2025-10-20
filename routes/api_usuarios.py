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

    data = request.get_json()

    if not data or not all(key in data for key in ['nome', 'email', 'senha', 'tipo']):

        return jsonify({ "error": "Dados inválidos, todos os campos são obrigatórios" }), 400

    conn = Connection('local')

    try:

        id_usuario = Usuarios(conn.connection_db).create(

            data['nome'],
            data['email'],
            data['senha'],
            data['tipo']

        )
        
        if id_usuario:

            return jsonify({ 

                "message": "Usuário cadastrado com sucesso!",
                "id_usuario": id_usuario

            }), 201
    
        else:

            return jsonify({"error": "Erro ao cadastrar usuário"}), 500

    except Exception as e:

        return jsonify({ "error": f"Erro no servidor: {e}" }), 500

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
def delete ():

    pass