from flask import Blueprint, request, redirect, jsonify
from controllers.comprador_controller import Compradores
from controllers.materiais_controller import Materiais
from controllers.feedback_controller import Feedbacks
from controllers.comentarios_controller import Comentarios
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
    finally:
        if conn:
            conn.close()
    
@api_get.route("/feedbacks", methods=["GET"])
def get_feedbacks():
    try:
        conn = Connection('local')
        feedbacks = Feedbacks(conn.connection_db).get_all()
        return jsonify(feedbacks), 200
    except Exception as e:
        print(f"Erro ao buscar feedbacks: {e}")
        return jsonify({"erro": "Ocorreu um erro interno no servidor"}), 500
    finally:
        if conn:
            conn.close()
    

@api_get.route("/materiais", methods=["GET"])
def get_materiais():
    """
    Rota para obter a lista completa de materiais do catálogo.
    """
    try:
        conn = Connection('local')
        materiais = Materiais(conn.connection_db).get_all()
        conn.close()
        return jsonify(materiais), 200
    except Exception as e:
        print(f"Erro ao buscar materiais: {e}")
        return jsonify({"erro": "Ocorreu um erro interno no servidor"}), 500
    finally:
        if conn:
            conn.close()
    
@api_get.route("/comprador/<material>", methods=["GET"])
def get_by_material(material):
    try:
        conn = Connection('local')
        compradores = Compradores(conn.connection_db).get_by_materials(material)
        return jsonify(compradores), 200
    except Exception as e:
        print(f"Erro ao buscar ompradores por material: {e}")
        return jsonify({"erro":"Ocorreu um erro"}), 500
    finally:
        if conn:
            conn.close()
    
@api_get.route("/feedback-tags/<cnpj>", methods=["GET"])
def get_feedback_tags_vendedor(cnpj):
    try:
        conn = Connection('local')
        feedbacks_tags = Comentarios(conn.connection_db).get_feedback_tags(cnpj)
        return jsonify(feedbacks_tags), 200
    except Exception as e:
        print (e)
        return jsonify({"erro":"falha ao buscar dados"})
    finally:
        if conn:
            conn.close()

@api_get.route("/comentarios-livres/<cnpj>")
def get_comentarios(cnpj):
    try:
        conn = Connection('local')
        comentarios = Comentarios(conn.connection_db).get_comentarios(cnpj)
        return jsonify(comentarios), 200
    except Exception as e:
        return jsonify({"erro":"falha ao buscar dados","ERROR":e})
    finally:
        if conn:
            conn.close()