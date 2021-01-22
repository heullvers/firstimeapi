from flask import Flask, request
from flask import jsonify
from main import getDados, verificaLink, extrairEstatisticas, maquina, predizer
from flask_apscheduler import APScheduler
import time
import requests

from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

scheduler = APScheduler()
dados = getDados()
print('Jogos capturados')
machine = maquina() 
print('Máquina treinada')

def atualiza():
    global dados
    dados = getDados()

@app.route('/')
def index():
    return "Hello World!"

@app.route('/jogos', methods=['GET'])
def jogos():
    return jsonify(dados)


@app.route('/verificarlink/', methods=['POST'])
def default():
    link = request.args.get('link', '')
    resultadoLink = verificaLink(link)
    if(resultadoLink):
        resultadoExtracao = extrairEstatisticas(link)
        predicao = predizer(resultadoExtracao)

        resultado = predicao[0]
        probabilidadeDerrota = predicao[1]
        probabilidadeEmpate = predicao[2]
        probabilidadeVitoria = predicao[3]

        return jsonify(predicao)

    else:
        return '0'
    #return verificaLink(link)

if __name__ == "__main__":
    scheduler.add_job(id="Scheduled task", func=atualiza, trigger="interval", seconds= 30)
    scheduler.start()
    app.run()
    
