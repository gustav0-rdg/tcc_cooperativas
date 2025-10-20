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
    return render_template("login-catador.html")

@pages.route("/cadastro-catador", methods=["GET"])
def pagina_cadastro_catador():
    return render_template("cadastro-catador.html")

@pages.route("/pagina-inicial", methods=["GET"])
def menu_principal():
    return render_template("tela-inicial.html")

@pages.route("/buscar-comprador", methods=['GET'])
def pagina_buscar_comprador():
    return render_template("buscar-comprador.html")

@pages.route("/registrar-venda")
def pagina_registrar_venda():
    return render_template("registrar-venda.html")

@pages.route("/pagina-informacoes")
def pagina_informacoes():
    return render_template("pagina_informacoes.html")
@pages.route("/editar-informacoes")
def pagina_editar_informacoes():
    return render_template("editar-informacoes.html")

@pages.route("/recuperar-senha")
def pagina_recuperar_senha():
    return render_template("recuperar-senha.html")
