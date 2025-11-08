from flask import Blueprint, jsonify, request
from data.connection_controller import Connection
from controllers.tokens_controller import Tokens
from controllers.usuarios_controller import Usuarios
from controllers.cooperativa_controller import Cooperativa
from controllers.cooperados_controller import Catadores
api_cooperados = Blueprint(
    
    'api_cooperados', 
    __name__, 
    url_prefix='/api/cooperados'
    
)

@api_cooperados.route("/get/<identificador>")
def get_cooperados(identificador: int):
    token = request.headers.get('authorization')
    if not token:
        return jsonify({'error':'"Token" é um parametro obrigatório'}),400
    
    conn = Connection('local')
    try:
        data_token = Tokens(conn.connection_db).validar(token)
        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({ 'error': '"Token" inexistente ou inválido'}), 400
        user = Usuarios(conn.connection_db).get_by_id(data_token['id_usuario'])
        if not user['tipo'] in ['cooperativa', 'gestor', 'root']:
            return jsonify({'error': 'Você não tem permissão para realizar tal ação'}), 403
        elif user['tipo'] == 'cooperativa':
            dados_cooperativa_logada = Cooperativa(conn.connection_db).get_cooperativa_by_user_id(user['id_usuario'])
            if not dados_cooperativa_logada:
                return jsonify({'error': 'Cooperativa associada a este usuário não encontrada'}), 404
            
            if (identificador != dados_cooperativa_logada['id_usuario']):
                return jsonify({'error':'Acesso negado. Você só pode consultar os dados da sua própria cooperativa.'}),403
        dados_cooperativa = Cooperativa(conn.connection_db).get_cooperativa_by_user_id(identificador)
        print(dados_cooperativa)
    except Exception as e:
        return jsonify({'error': f'Erro no servidor {e}'}),500
    
    finally:
        conn.close()