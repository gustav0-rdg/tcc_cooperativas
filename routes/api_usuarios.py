from flask import Blueprint, request, jsonify
from controllers.usuarios_controller import Usuarios
from data.connection_controller import Connection

api_usuarios = Blueprint(
    
    'api_usuarios', 
    __name__, 

    url_prefix='/api/usuarios'
    
)

@api_usuarios.route('/login', methods=['POST'])
def login ():

    data = request.get_json()

    email = data.get('email')
    senha = data.get('senha')

    if not email or not senha:

        return jsonify({ 'texto': 'Email e Senha são obrigatórios e essenciais' }), 400

    conn = Connection('local')
    token_sessao = Usuarios(conn.connection_db).autenticar(email, senha)
    conn.close()
    
    if token_sessao:

        return jsonify({ 'token': token_sessao }), 200
    
    else:

        return jsonify({ 'texto': 'Email ou Senha inválidos' }), 401