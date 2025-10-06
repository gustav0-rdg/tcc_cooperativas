from flask import redirect, Blueprint, request

api_post = Blueprint('api_post', __name__, url_prefix="/post")

@api_post.route("/cooperativa", methods=["POST"])
def cadastrar_cooperativa():
    cnpj = request.form.get("cnpj")
    nome = request.form.get("nome")
    telefone = request.form.get("telefone")
    data_nascimento = request.form.get("data")
    return redirect("/login")
