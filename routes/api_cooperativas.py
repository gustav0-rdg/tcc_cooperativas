from flask import Blueprint, request, jsonify
from controllers.tokens_controller import Tokens
from data.connection_controller import Connection
from controllers.usuarios_controller import Usuarios
from controllers.cooperativa_controller import Cooperativa

api_cooperativas = Blueprint(
    
    'api_cooperativas', 
    __name__, 

    url_prefix='/api/cooperativas'
    
)

@api_cooperativas.route('/alterar-aprovacao/<id_cooperativa>', methods=['POST'])
def alterar_aprovacao (id_cooperativa:int):

    if not id_cooperativa.isdigit():
        return jsonify({ 'error': '"id_cooperativa" é inválido' }), 400
    
    id_cooperativa = int(id_cooperativa)

    aprovacao = request.get_json().get('aprovacao')

    if not aprovacao or not isinstance(aprovacao, bool):
        return jsonify({ 'error': '"aprovacao" deve ser do tipo Booleano' }), 400

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({ 'error': '"token" é parâmetro obrigatório' }), 400

    conn = Connection()

    try:

        data_token = Tokens(conn.connection_db).validar(token)

        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400
        
        if not Usuarios(conn.connection_db).get_by_id(data_token['id_usuario'])['tipo'] in ['gestor', 'root']:
            return jsonify({ 'error': 'Você não tem permissão para realizar tal ação' }), 403
        
        match Cooperativa(conn.connection_db).alterar_aprovacao(id_cooperativa, aprovacao):

            # 404 - Cooperativa não encontrada

            case None:
                return jsonify({ 'error': 'Usuário não encontrado' }), 404

            # 200 - Aprovação alterada

            case True:
                return jsonify({ 'texto': 'Aprovação da cooperativa alterada' }), 200

            # 500 - Erro ao alterar a aprovação da cooperativa

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500

    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()

@api_cooperativas.route('/vincular-cooperado', methods=['POST'])
def vincular_cooperado ():

    data_cooperado = request.get_json()

    if not data_cooperado or not all(key in data_cooperado for key in ['nome', 'email', 'senha', 'cpf', 'telefone', 'endereco', 'cidade', 'estado']):
        
        return jsonify({ 'error': 'Dados de cadastro inválidos, todos os campos são obrigatórios: nome, senha, email, cpf, telefone, endereco, cidade e estado' }), 400
    
    if len(data_cooperado['senha']) < 8:
        return jsonify({ 'texto': 'A senha deve ter no minímo 8 caractéres' }), 400

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400

    conn = Connection('local')

    try:

        data_token = Tokens(conn.connection_db).validar(token)

        # Token Inválido

        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({ 'error': '"token" inválido' }), 400

        data_adm_cooperativa = Usuarios(conn.connection_db).get_by_id(data_token['id_usuario'])

        # Autor da requisição inválido

        if not data_adm_cooperativa or data_adm_cooperativa['tipo'] != 'cooperativa':
            return jsonify({ 'error': 'Você não tem permissão para realizar tal ação' }), 403
        
        data_cooperativa = Cooperativa(conn.connection_db).get_by_usuario(data_adm_cooperativa['id_usuario'])

        id_cooperado = Cooperativa(conn.connection_db).vincular_cooperado(

            data_cooperativa['id_cooperativa'],

            data_cooperado['nome'],
            data_cooperado['email'],
            data_cooperado['senha'],
            
            data_cooperado['cpf'],
            data_cooperado['telefone'],
            data_cooperado['endereco'],
            data_cooperado['cidade'],
            data_cooperado['estado']

        )

        match id_cooperado:

            # 409 - Email já cadastrado

            case None:
                return jsonify({ 'error': 'Email já cadastrado' }), 409

            # 200 - Usuário cooperado vinculado

            case _ if isinstance(id_cooperado, int):
                
                return jsonify({ 'texto': 'Cooperado vinculado' }), 200

            # 500 - Erro ao vincular usuário cooperado

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500

    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()