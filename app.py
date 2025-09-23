from flask import Flask
from routes.pages import pages

app = Flask(__name__)

app.register_blueprint(pages)


app.run(debug=True)