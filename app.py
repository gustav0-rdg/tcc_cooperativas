from flask import Flask
from routes.pages import pages
from routes.api_post import api_post
from routes.api_get import api_get

app = Flask(__name__)

app.register_blueprint(pages)
app.register_blueprint(api_post)
app.register_blueprint(api_get)

app.run(debug=True)