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

@api_cooperados.route("/get/<identificador>", methods=["POST"])
def get_cooperados(identificador: int):
    token = request.headers.get('authorization')
    if not token:
        return jsonify({'error':'"Token" é um parametro obrigatório'}),400
    
    conn = Connection('local')
    try:
        data_token = Tokens(conn.connection_db).validar(token)
        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({ 'error': '"Token" inexistente ou inválido'}), 400
        user = Usuarios(conn.connection_db).get(data_token['id_usuario'])
        if not user['tipo'] in ['cooperativa', 'gestor', 'root']:
            return jsonify({'error': 'Você não tem permissão para realizar tal ação'}), 403
        elif user['tipo'] == 'cooperativa':
            dados_cooperativa_logada = Cooperativa(conn.connection_db).get_cooperativa_by_user_id(user['id_usuario'])
            if not dados_cooperativa_logada:
                return jsonify({'error': 'Cooperativa associada a este usuário não encontrada'}), 404
            #  CORRIGIR DEPOIS BRUHHHH
            
            # if (identificador != dados_cooperativa_logada['id_cooperativa']):
            #     return jsonify({'error':'Acesso negado. Você só pode consultar os dados da sua própria cooperativa.'}),403
        cooperados = Catadores(conn.connection_db).get_all(dados_cooperativa_logada['id_cooperativa'])
        return cooperados
    
    except Exception as e:
        return jsonify({'error': f'Erro no servidor {e}'}),500
    
    finally:
        conn.close()

@api_cooperados.route('/delete/<id_cooperado>')
def delete_cooperado(id_cooperado):
    token = request.headers.get('authorization')
    if not token:
        return jsonify({'erro':'"Token" é um parametro obrigatório'}),400
    conn = Connection('local')
    try:
        data_token = Tokens(conn.connection_db).validar(token)
        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({'error':'"Token" inexistente ou inválido'}),400
        user = Usuarios(conn.connection_db).get(data_token['id_usuario'])
        if not user['tipo'] in ['cooperativa', 'gestor', 'root']:
            return jsonify({'error':'você não tem permissão pra realizar tal ação'})
        elif user['tipo'] == 'cooperativa':
            
    except Exception as e:
        return jsonify({'error': f'Erro no servidor {e}'}),500
    
    finally:
        conn.close()    

@api_cooperados.route('/get/<identificador>/<nome>', methods=["POST"])
def search_cooperado(identificador, nome):
    token = request.headers.get('authorization')
    if not token:
        return jsonify({'error':'"Token" é um parametro obrigatório'}),400
    
    conn = Connection('local')
    try:
        data_token = Tokens(conn.connection_db).validar(token)
        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({ 'error': '"Token" inexistente ou inválido'}), 400
        user = Usuarios(conn.connection_db).get(data_token['id_usuario'])
        if not user['tipo'] in ['cooperativa', 'gestor', 'root']:
            return jsonify({'error': 'Você não tem permissão para realizar tal ação'}), 403
        elif user['tipo'] == 'cooperativa':
            dados_cooperativa_logada = Cooperativa(conn.connection_db).get_cooperativa_by_user_id(user['id_usuario'])
            if not dados_cooperativa_logada:
                return jsonify({'error': 'Cooperativa associada a este usuário não encontrada'}), 404
            #  CORRIGIR DEPOIS BRUHHHH
            
            # if (identificador != dados_cooperativa_logada['id_cooperativa']):
            #     return jsonify({'error':'Acesso negado. Você só pode consultar os dados da sua própria cooperativa.'}),403
        cooperados = Catadores(conn.connection_db).search_cooperado(dados_cooperativa_logada['id_cooperativa'], nome)
        return cooperados
    
    except Exception as e:
        return jsonify({'error': f'Erro no servidor {e}'}),500
    
    finally:
        conn.close()