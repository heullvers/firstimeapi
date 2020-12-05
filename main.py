from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import time

def getDados():

    url = 'https://www.flashscore.com.br/'

    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    button = driver.find_element_by_xpath('//*[@id="live-table"]/div[1]/div[1]/div[2]')
    button.click()

    html = driver.execute_script("return document.documentElement.outerHTML")
    #driver.quit()

    headers = []
    soup = BeautifulSoup(html, 'html.parser')
    head = soup.findAll(True, {'class': ['event__header', 'event__match']})

    i = 1
    for h in head:
        if(h['class'][0] == 'event__header'):
            visualization = h.find('div', class_="event__expander")
            title = visualization['title']
            if(title == 'Exibir todos os jogos desta competição!'):
                headers.append(i)
        i += 1


    xpathBase = '//*[@id="live-table"]/div[2]/div/div/div['
    xpathComplemento = ']/div[3]'

    xpaths = []
    for h in headers:
        xpath = xpathBase + str(h) + xpathComplemento
        xpaths.append(xpath)


    xpaths.reverse()
    for xpath in xpaths:
        button = driver.find_element_by_xpath(xpath)
        driver.execute_script("arguments[0].click();", button)


    html = driver.execute_script("return document.documentElement.outerHTML")
    soup = BeautifulSoup(html, 'html.parser')
    head = soup.findAll(True, {'class': ['event__header', 'event__match']})

    driver.quit()

    i = 0
    headers = []
    matchs = []

    campeonatos = []
    jogos = []

    for h in head:
        if(h['class'][0] == 'event__header'):
            headers.append(i)
            campeonatos.append(h)
        else:
            matchs.append(i)
            jogos.append(h)
        i += 1

    tamanhoHeaders = []

    lenHeader = len(headers)

    for i in range(lenHeader - 1):
        tamanho = headers[i+1] - headers[i] - 1
        tamanhoHeaders.append(tamanho)
        i += 1

    ultimoHeader = matchs[len(matchs) - 1] - headers[len(headers) -1 ]
    tamanhoHeaders.append(ultimoHeader)

    aux = 0
    i = 0
    jogos_em_andamento = []

    for camp in campeonatos:
        pais = camp.find('span', class_="event__title--type")
        pais = pais.text
        nomeCampeonato = camp.find('span', class_="event__title--name")
        nomeCampeonato = nomeCampeonato.text
        campeonato = pais + ': ' + nomeCampeonato
        for j in range(tamanhoHeaders[i]):
            jogo = jogos[aux]
            aux += 1
            
            situacao = jogo.find('div', class_="event__stage")
            if(situacao):
                if((situacao.text != 'Encerrado') and (situacao.text != 'Adiado') and (situacao.text != 'Atrasado')):
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
                    json['Campeonato'] = campeonato
                    json['linkEstatistica'] = link_jogo_estatistica
                    json['linkOdds'] = link_jogo_odds
                    jogos_em_andamento.append(json)
        i += 1
    return jogos_em_andamento

resultados = getDados()