from flask import Flask
from routes.pages import pages
from routes.auth.auth_routes import auth
from routes.api_post import api_post

app = Flask(__name__)

app.register_blueprint(pages)
app.register_blueprint(auth)
app.register_blueprint(api_post)

app.run(debug=True)