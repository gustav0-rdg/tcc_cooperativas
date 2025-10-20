from flask import Flask
from routes.pages import pages
# from routes.auth.auth_routes import auth
from routes.api_post import api_post
from routes.api_get import api_get
from routes.api_usuarios import api_usuarios

app = Flask(__name__)

app.register_blueprint(pages)
# app.register_blueprint(auth)
app.register_blueprint(api_post)
app.register_blueprint(api_get)
app.register_blueprint(api_usuarios)

app.run(debug=True)