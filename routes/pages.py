from flask import render_template, Blueprint

pages = Blueprint('pages', __name__)

# Selecionar se é catador ou cooperativa
@pages.route("/", methods=["GET"])
def pagina_inicial():
    return render_template("index.html")

@pages.route("/cadastro", methods=["GET"])
def pagina_cadastro():
    return render_template("cadastro.html")

@pages.route("/login", methods=["GET"])
def pagina_login():
    return render_template("login.html")

@pages.route("/login-catador", methods=["GET"])
def pagina_login_catador():
    return render_template("")

@pages.route("/cadastro-catador", methods=["GET"])
def pagina_cadastro_catador():
    return render_template("cadastro-catador.html")
