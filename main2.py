from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import time

def getDados():

    dicBrasilA = {'nome': 'Brasileiro Série A', 'url': 'https://www.flashscore.com.br/futebol/brasil/serie-a/'}
    dicBrasilB = {'nome': 'Brasileiro Série B', 'url': 'https://www.flashscore.com.br/futebol/brasil/serie-b/'}
    dicBrasilC = {'nome': 'Brasileiro Série C', 'url': 'https://www.flashscore.com.br/futebol/brasil/serie-c/'}
    dicBrasilD = {'nome': 'Brasileiro Série D', 'url': 'https://www.flashscore.com.br/futebol/brasil/serie-d/'}

    dicAlemao = {'nome': 'Bundesliga', 'url': 'https://www.flashscore.com.br/futebol/alemanha/bundesliga/'}
    dicEspanhol = {'nome': 'La Liga', 'url': 'https://www.flashscore.com.br/futebol/espanha/laliga/'}
    dicIngles = {'nome': 'Premier League', 'url': 'https://www.flashscore.com.br/futebol/inglaterra/campeonato-ingles/'}
    dicItaliano = {'nome': 'Tim', 'url': 'https://www.flashscore.com.br/futebol/italia/serie-a/'}

    lista = []
    lista.append(dicBrasilA)
    lista.append(dicBrasilB)
    lista.append(dicBrasilC)
    lista.append(dicBrasilD)

    lista.append(dicAlemao)
    lista.append(dicEspanhol)
    lista.append(dicIngles)
    lista.append(dicItaliano)

    jogos_em_andamento = []
    for campeonato in lista:
        options = webdriver.ChromeOptions()
        options.headless = True
        driver = webdriver.Chrome(options=options)
        driver.get(campeonato['url'])
        html = driver.execute_script("return document.documentElement.outerHTML")
        driver.quit()

        soup = BeautifulSoup(html, 'html.parser')
        jogos_de_hoje = soup.find('div', class_="tabs--live")

        if(jogos_de_hoje): #está acontecendo jogos no dia atual
            tabela = soup.find('div', class_='leagues--live contest--leagues')
            tabela_dois = tabela.find('div', class_="sportName soccer")
            jogos = tabela_dois.find_all('div', class_="event__match")

            for jogo in jogos:
                situacao = jogo.find('div', class_="event__stage")
                if(situacao):
                    if(situacao.text != 'Encerrado'):
                        link_base = 'https://www.flashscore.com.br/jogo/'
                        
                        link_complementar_estatistica = '/#estatisticas-de-jogo;1'
                        link_complementar_odds = '/#comparacao-de-odds;1x2-odds;1-tempo'

                        link_jogo = jogo['id']
                        link_jogo = link_jogo[4:]

                        link_jogo_estatistica = link_base + link_jogo + link_complementar_estatistica
                        link_jogo_odds = link_base + link_jogo + link_complementar_odds

                        #situacao.text == numero ou 'intervalo'
                        ##Variável situacao
                        situacao = situacao.text
                        situacao = situacao.replace('\xa0', '')

                        ##Variável time_mandante, time_visitante
                        times = jogo.find_all('div', class_="event__participant")
                        time_mandante = times[0].text
                        time_visitante = times[1].text

                        placar = jogo.find('div', class_='event__scores')
                        valores = placar.find_all('span')

                        #Variável gols_time_mandante, gols_time_visitante
                        gols_time_mandante = valores[0].text
                        gols_time_visitante = valores[1].text

                        json = {}
                        json['situacao'] = situacao
                        json['timeMandante'] = time_mandante
                        json['timeVisitante'] = time_visitante
                        json['GolsMandante'] = gols_time_mandante
                        json['GolsVisitante'] = gols_time_visitante
                        json['Campeonato'] = campeonato['nome']
                        json['linkEstatistica'] = link_jogo_estatistica
                        json['linkOdds'] = link_jogo_odds
                        jogos_em_andamento.append(json)

    return jogos_em_andamento

dados = getDados()
#print(dados)