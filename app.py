from flask import Flask, request, redirect, session, render_template
from dotenv import load_dotenv
from os import getenv

# Carrega as variáveis do arquivo '.env'
load_dotenv()

# Importa as rotas
from routes.pages import pages
from routes.api_post import api_post
from routes.api_get import api_get
from routes.api_usuarios import api_usuarios
from routes.api_cooperativas import api_cooperativas
from routes.api_cooperados import api_cooperados
from data.connection_controller import Connection
from controllers.tokens_controller import Tokens
from controllers.usuarios_controller import Usuarios

app = Flask(__name__)

app.register_blueprint(pages)
app.register_blueprint(api_post)
app.register_blueprint(api_get)
app.register_blueprint(api_usuarios)
app.register_blueprint(api_cooperativas)
app.register_blueprint(api_cooperados)

# Rotas públicas que não requerem autenticação
ROTAS_PUBLICAS = {
    '/',
    '/cadastro',
    '/registrar_cooperativa',
    '/login',
    '/login-cooperado',
    '/cadastro-cooperado',
    '/login-admin',
    '/recuperar-senha',
    '/redefinir-senha',
    '/Termos-de-Uso'
}

# Rotas que exigem um usuário do tipo 'gestor' ou 'root'
ROTAS_GESTOR = {
    '/pagina-inicial/gestor',
    '/visualizar-cooperativas',
    '/gerenciar-cadastros',
    '/gerenciar-gestores'
}


@app.before_request
def verificar_autenticacao():
    # Permite rotas públicas
    if request.path in ROTAS_PUBLICAS:
        return

    # Permite arquivos estáticos
    if request.path.startswith('/static/'):
        return

    # Rotas de API
    if request.path.startswith('/api/') or \
       request.path.startswith('/get/') or \
       request.path.startswith('/post/'):
        return

    if request.endpoint is None:
        return

    token = request.headers.get('Authorization') or request.cookies.get('session_token')

    # Se não há token, redireciona para a página apropriada
    if not token:
        if request.path in ROTAS_GESTOR:
            return redirect('/login-admin')
        return redirect('/')

    conn = Connection('local')
    try:
        # Valida o token
        data_token = Tokens(conn.connection_db).validar(token)
        
        # Se o token for inválido ou não for de sessão
        if not data_token or data_token.get('tipo') != 'sessao':
            conn.close()
            if request.path in ROTAS_GESTOR:
                return redirect('/login-admin')
            return redirect('/')

        if request.path in ROTAS_GESTOR:
            usuario = Usuarios(conn.connection_db).get(data_token['id_usuario'])
            conn.close() 
            
            if not usuario or usuario.get('tipo') not in ['gestor', 'root']:
                return redirect('/login-admin')
            return

        # Para outras rotas protegidas
        conn.close()
        return 

    except Exception as e:
        print(f"Erro no middleware: {e}")
        if conn:
            conn.close()
        return redirect('/')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run(debug=True)
