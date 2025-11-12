from flask import Flask, request, redirect, session
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

@app.before_request
def verificar_autenticacao():
    # Permite rotas públicas
    if request.path in ROTAS_PUBLICAS:
        return

    # Permite arquivos estáticos
    if request.path.startswith('/static/'):
        return

    # Permite rotas de API (elas fazem verificação interna)
    if request.path.startswith('/api/') or \
       request.path.startswith('/get/') or \
       request.path.startswith('/post/'):
        return

    # Para outras rotas, verifica se há token válido (header ou cookie)
    token = request.headers.get('Authorization') or request.cookies.get('session_token')
    
    if not token:
        return redirect('/')

    conn = Connection('local')
    try:
        if not request.headers.get('Authorization') and request.cookies.get('session_token'):
            data_token = Tokens(conn.connection_db).validar(request.cookies.get('session_token'))
            if not data_token:
                conn.close()
                return redirect('/')
        
        conn.close()
        return 

    except Exception as e:
        print(f"Erro no middleware: {e}")
        if conn:
            conn.close()
        return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
