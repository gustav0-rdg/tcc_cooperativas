from flask import redirect, Blueprint, request, jsonify

api_post = Blueprint('api_post', __name__, url_prefix="/post")

@api_post.routes("/catador", methods=["POST"])
def cadastrar_catador():
    cpf = request.form.get("cpf")
    nome = request.form.get("nome")
    telefone = request.form.get("telefone")
    data_nascimento = request.form.get("data")
    return redirect("/login")

@api_post.route("/dados-venda", methods=["POST"])
def postar_dados_de_venda():
    dados_recebidos = request.get_json()
    print(dados_recebidos)
    return jsonify({"status": "sucesso", "mensagem": "Dados da venda recebidos!"}), 200
