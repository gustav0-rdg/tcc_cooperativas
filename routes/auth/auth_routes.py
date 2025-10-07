from flask import Blueprint, request

auth = Blueprint('auth', __name__, url_prefix="/auth")

@auth.routes("/catador", methods=["POST"])
def login_catador():
    cpf = request.form.get("cpf")
    senha = request.form.get("senha")

@auth.routes("/cooperativa", methods=["POST"])
def login_cooperativa():
    cnpj = request.form.get("cnpj")
    senha = request.form.get("senha")