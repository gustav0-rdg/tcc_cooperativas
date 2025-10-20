from flask import Blueprint, request, redirect, jsonify
from controllers.comprador_controller import Compradores
from controllers.materiais_controller import Materiais
from controllers.feedback_controller import Feedbacks
from data.connection_controller import Connection
api_get = Blueprint('api_get', __name__, url_prefix='/get')

@api_get.route("/compradores", methods=["GET"])
def get_compradores():
    try:
        conn = Connection('local')
        compradores = Compradores(conn.connection_db).get_all()
        return jsonify(compradores), 200
    except Exception as e:
        print(f"Erro ao buscar compradores: {e}")
        return jsonify({"erro": "Ocorreu um erro interno no servidor"}), 500
    
@api_get.route("/feedbacks", methods=["GET"])
def get_feedbacks():
    try:
        conn = Connection('local')
        feedbacks = Feedbacks(conn.connection_db).get_all()
        return jsonify(feedbacks), 200
    except Exception as e:
        print(f"Erro ao buscar feedbacks: {e}")
        return jsonify({"erro": "Ocorreu um erro interno no servidor"}), 500
    

@api_get.route("/materiais", methods=["GET"])
def get_materiais():
    """
    Rota para obter a lista completa de materiais do catálogo.
    """
    try:
        conn = Connection('local')
        # Chama o método do controller para buscar os dados
        materiais = Materiais(conn.connection_db).get_all()
        # Retorna os dados em formato JSON com status 200 (OK)
        conn.close()
        return jsonify(materiais), 200
    except Exception as e:
        # Em caso de erro, loga no console e retorna um erro 500
        print(f"Erro ao buscar materiais: {e}")
        return jsonify({"erro": "Ocorreu um erro interno no servidor"}), 500