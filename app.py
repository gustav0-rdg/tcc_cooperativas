from flask import Flask
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

app = Flask(__name__)

app.register_blueprint(pages)
app.register_blueprint(api_post)
app.register_blueprint(api_get)
app.register_blueprint(api_usuarios)
app.register_blueprint(api_cooperativas)

if __name__ == "__main__":
    app.run(debug=True)