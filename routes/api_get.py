from flask import Blueprint, request, redirect, jsonify
from controllers.comprador_controller import Compradores
api_get = Blueprint('api_get', __name__, url_prefix='/get')

@api_get.route("/compradores", methods=["GET"])
def get_compradores():
    compradores = Compradores.get_all()
    return jsonify(compradores)

