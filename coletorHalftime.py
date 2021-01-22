from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import time
from Partida import Partida
import csv

def extrairEstatisticas(link):
    
    estatisticas = link

    options = webdriver.FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get(estatisticas)
    time.sleep(2)

    html = driver.execute_script("return document.documentElement.outerHTML")
    driver.quit()

    soup = BeautifulSoup(html, 'html.parser')

    placar = soup.find('div', class_="match-info")
    placar = placar.find_all('span', class_="scoreboard")

    ##Descobrir o placar atual do jogo
    golsMandante = placar[0].text
    golsVisitante = placar[1].text

    print(golsMandante)
    print(golsVisitante)

    diferencaGolsPrimeiroTempo = int(golsMandante) - int(golsVisitante)

    #Variável
    placarAtual = None

    if(golsMandante == golsVisitante):
        placarAtual = 'E'
    elif(golsMandante > golsVisitante):
        placarAtual = 'V'
    else:
        placarAtual = 'D'

    print(placarAtual)
    print(diferencaGolsPrimeiroTempo)


    ##Descobrir as estatísticas
    quadro = soup.find('div', id="tab-statistics-1-statistic")

    parciais = quadro.find_all('div', class_="statRow")

    dicionario = {}

    for parcial in parciais:
        linha = parcial.find('div', class_="statTextGroup")
        casa = (linha.find('div', class_="statText--homeValue")).text
        estatistica = (linha.find('div', class_="statText--titleValue")).text
        visitante = (linha.find('div', class_="statText--awayValue")).text

        if(estatistica == 'Posse de bola'):
            casa = casa.replace('%', '')
            visitante = visitante.replace('%', '')
        
        dicionario[estatistica] = [casa, visitante]


    ##Variáveis
    if('Posse de bola' in dicionario):
        posseDebolaM = dicionario['Posse de bola'][0]
        posseDebolaV = dicionario['Posse de bola'][1]
    else:
        posseDebolaM = None
        posseDebolaV = None

    if('Finalizações' in dicionario):
        finalizacoesM = dicionario['Finalizações'][0]
        finalizacoesV = dicionario['Finalizações'][1]
    else:
        finalizacoesM = None
        finalizacoesV = None

    if('Chutes fora' in dicionario):
        chutesForaM = dicionario['Chutes fora'][0]
        chutesForaV = dicionario['Chutes fora'][1]
    else:
        chutesForaM = None
        chutesForaV = None

    if('Escanteios' in dicionario):
        escanteiosM = dicionario['Escanteios'][0]
        escanteiosV = dicionario['Escanteios'][1]
    else:
        escanteiosM = None
        escanteiosV = None

    if('Impedimentos' in dicionario):
        impedimentosM = dicionario['Impedimentos'][0]
        impedimentosV = dicionario['Impedimentos'][1]
    else:
        impedimentosM = None
        impedimentosV = None

    if('Cartões vermelhos' not in dicionario):
        dicionario['Cartões vermelhos'] = ['0','0']
        cartoesVermelhosM = dicionario['Cartões vermelhos'][0]
        cartoesVermelhosV = dicionario['Cartões vermelhos'][1]
    else:
        cartoesVermelhosM = dicionario['Cartões vermelhos'][0]
        cartoesVermelhosV = dicionario['Cartões vermelhos'][1]

    ##Descobrir as odds

    options = webdriver.FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get(estatisticas)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)


    html = driver.execute_script("return document.documentElement.outerHTML")
    driver.quit()
    soup = BeautifulSoup(html, 'html.parser')

    
    oddsPrimeiroTempo = soup.find('table', id="default-live-odds")
    oddsPrimeiroTempo = oddsPrimeiroTempo.find('tbody')
    oddsPrimeiroTempo = oddsPrimeiroTempo.find('tr')
    oddsPrimeiroTempo = oddsPrimeiroTempo.find_all('span', class_="odds-wrap")


    ##Variáveis
    oddCasa = oddsPrimeiroTempo[0].text
    oddEmpate = oddsPrimeiroTempo[1].text
    oddVisitante = oddsPrimeiroTempo[2].text

    dicionario['oddCasa'] = oddCasa
    dicionario['oddEmpate'] = oddEmpate
    dicionario['oddVisitante'] = oddVisitante

    dicionario['diferencaGols'] = diferencaGolsPrimeiroTempo

    print(dicionario)
