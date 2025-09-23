from flask import Flask, render_template, redirect

app = Flask(__name__)

# Selecionar se é catador ou cooperativa
@app.route("/")
def pagina_inicial():
    return render_template("index.html")

@app.route("/cadastro")
def pagina_cadastro():
    return render_template("cadastro.html")

app.run(debug=True)