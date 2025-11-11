from flask import render_template, Blueprint, redirect, request, url_for
from controllers.tokens_controller import Tokens
from data.connection_controller import Connection
from routes.auth.auth_routes import token_required

pages = Blueprint('pages', __name__)

# Selecionar se é cooperado ou cooperativa
@pages.route("/", methods=["GET"])
def pagina_inicial():
    return render_template("index.html")

@pages.route("/cadastro", methods=["GET"])
def pagina_cadastro():
    return render_template("cadastro.html")

@pages.route("/registrar_cooperativa", methods=["POST"])
def formulario_cadastro():
    return render_template("cadastro.html")

@pages.route("/login", methods=["GET"])
def pagina_login():
    return render_template("login-cooperativa.html")

@pages.route("/login-cooperado", methods=["GET"])
def pagina_login_cooperado():
    return render_template("login-cooperado.html")

@pages.route("/cadastro-cooperado", methods=["GET"])
def pagina_cadastro_cooperado():
    return render_template("cadastro-cooperado.html")

@pages.route("/pagina-inicial", methods=["GET"])
@token_required
def menu_principal():
    return render_template("tela-inicial.html")

@pages.route("/buscar-comprador", methods=['GET'])
@token_required
def pagina_buscar_comprador():
    return render_template("buscar-comprador.html")

@pages.route("/registrar-venda")
@token_required
def pagina_registrar_venda():
    return render_template("registrar-venda.html")

@pages.route("/pagina-informacoes")
@token_required
def pagina_informacoes():
    return render_template("pagina-informacoes.html")

@pages.route("/editar-informacoes")
@token_required
def pagina_editar_informacoes():
    return render_template("editar-informacoes.html")

@pages.route("/pagina-inicial/gestor")
@token_required
def pagina_inicial_gestor():
    return render_template("pagina-inicial-gestor.html")

@pages.route("/visualizar-cooperativas")
@token_required
def pagina_cooperativas_gestor():
    return render_template("pagina-cooperativas-gestor.html")

@pages.route("/gerenciar-cadastros")
@token_required
def pagina_gerenciar_cadastros_gestor():
    return render_template("pagina-gerenciar-cadastros.html")

@pages.route("/recuperar-senha")
def pagina_recuperar_senha():
    return render_template("recuperar-senha.html")

@pages.route('/redefinir-senha')
def pagina_redefinir_senha():
    
    # Pega o token da URL. Exemplo: ?token=...
    token = request.args.get('token')

    if not token:
        return redirect('/')

    conn = Connection('local')

    try:

        # Valida o token
        data_token = Tokens(conn.connection_db).validar(token)
        
        if not data_token or data_token['tipo'] != 'recuperacao_senha' or data_token['usado'] == True:
            return redirect('/')
        
        return render_template('redefinir-senha.html', token=token)

    except Exception as e:
        
        return e
    
    finally:

        if conn:
            conn.close()

@pages.route("/Termos-de-Uso")
def pagina_termos_de_uso():
    return render_template("pagina-termo.html")

@pages.route("/gerenciar-gestores", methods=["GET"])
@token_required
def pagina_gerenciar_gestores():
    return render_template("gerenciar-gestores.html")

@pages.route("/login-admin" , methods=["GET"])
def pagina_login_admin():
    return render_template("login-admin.html")

@pages.route("/gerenciar-cooperados", methods=["GET"])
@token_required
def paginar_gerenciar_cooperados():
    return render_template("gerenciar-cooperados.html")