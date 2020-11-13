from flask import Flask
from flask import jsonify
from main import getDados
from flask_apscheduler import APScheduler
import time

app = Flask(__name__)
scheduler = APScheduler()

dados = ""

def atualiza():
    global dados
    dados = getDados()

@app.route("/")
def index():
    return "Hello World!"

@app.route("/jogos", methods=["GET"])
def jogos():
    return jsonify(dados)

if __name__ == "__main__":
    scheduler.add_job(id="Scheduled task", func=atualiza, trigger="interval", seconds= 30)
    scheduler.start()
    app.run()
    
