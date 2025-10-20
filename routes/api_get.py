from flask import Blueprint, request, redirect, jsonify
from controllers.comprador_controller import Compradores
from controllers.feedback_controller import Feedbacks
api_get = Blueprint('api_get', __name__, url_prefix='/get')

@api_get.route("/compradores", methods=["GET"])
def get_compradores():
    try:
        compradores = Compradores.get_all()
        return jsonify(compradores), 200
    except Exception as e:
        print(f"Erro ao buscar compradores: {e}")
        return jsonify({"erro": "Ocorreu um erro interno no servidor"}), 500
    
@api_get.route("/feedbacks", methods=["GET"])
def get_feedbacks():
    try:
        feedbacks = Feedbacks.get_all()
        return jsonify(feedbacks), 200
    except Exception as e:
        print(f"Erro ao buscar feedbacks: {e}")
        return jsonify({"erro": "Ocorreu um erro interno no servidor"}), 500