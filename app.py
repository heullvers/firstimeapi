from flask import Flask
from flask import jsonify
from main import getDados
import time

app = Flask(__name__)
dados = getDados()

@app.route("/")
def index():
    return "Hello World!"

@app.route("/jogos", methods=["GET"])
def jogos():
    return jsonify(dados)
    

if __name__ == "__main__":
    app.run()