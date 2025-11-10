from flask import render_template, Blueprint, redirect, request, url_for
from controllers.tokens_controller import Tokens
from data.connection_controller import Connection

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
    return render_template("pagina-informacoes.html")

@pages.route("/editar-informacoes")
def pagina_editar_informacoes():
    return render_template("editar-informacoes.html")

@pages.route("/pagina-inicial/gestor")
def pagina_inicial_gestor():
    return render_template("pagina-inicial-gestor.html")

@pages.route("/visualizar-cooperativas")
def pagina_cooperativas_gestor():
    return render_template("pagina-cooperativas-gestor.html")

@pages.route("/gerenciar-cadastros")
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
        return redirect(url_for('pages.pagina_login'))

    conn = Connection('local')

    try:

        # Valida o token
        data_token = Tokens(conn.connection_db).validar(token)
        
        if not data_token or data_token['tipo'] != 'recuperacao_senha':
            return redirect(url_for('views.pagina_login'))
        
        return render_template('redefinir_senha.html', token=token)

    except Exception as e:
        return redirect(url_for('pages.pagina_login'))
    
    finally:

        if conn:
            conn.close()

@pages.route("/Termos-de-Uso")
def pagina_termos_de_uso():
    return render_template("pagina-termo.html")

@pages.route("/gerenciar-gestores", methods=["GET"])
def pagina_gerenciar_gestores():
    return render_template("gerenciar-gestores.html")

@pages.route("/login-admin" , methods=["GET"])
def pagina_login_admin():
    return render_template("login-admin.html")

@pages.route("/gerenciar-cooperados", methods=["GET"])
def paginar_gerenciar_cooperados():
    return render_template("gerenciar-cooperados.html")