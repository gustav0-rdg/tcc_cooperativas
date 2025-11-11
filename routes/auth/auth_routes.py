from flask import Blueprint, request, redirect, url_for
from functools import wraps
from controllers.tokens_controller import Tokens
from data.connection_controller import Connection


auth = Blueprint('auth', __name__)

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('token')

        if not token:
            return redirect(url_for('pages.pagina_inicial'))

        conn = None
        try:
            conn = Connection('local')
            data_token = Tokens(conn.connection_db).validar(token)
            if not data_token or data_token['usado']:
                # Cria uma resposta de redirecionamento
                response = redirect(url_for('pages.pagina_inicial'))
                # Deleta o cookie
                response.set_cookie('token', '', expires=0)
                return response
        except Exception as e:
            print(f"An error occurred: {e}")
            return redirect(url_for('pages.pagina_inicial'))
        finally:
            if conn:
                conn.close()
        
        return f(*args, **kwargs)
    return decorated_function