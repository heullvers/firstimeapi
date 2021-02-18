from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import time


import pandas as pd
import numpy as np


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

                    link_jogo = jogo['id']
                    link_jogo = link_jogo[4:]

                    link_jogo_estatistica = link_base + link_jogo + link_complementar_estatistica

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
                #json['linkOdds'] = link_jogo_odds

                    jogos_em_andamento.append(json)
        i += 1
    return jogos_em_andamento


def verificaLink(link):
    ##verificar se possui estatisticas
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.get(link)
    time.sleep(2)
    html = driver.execute_script("return document.documentElement.outerHTML")
    driver.quit()
    soup = BeautifulSoup(html, 'html.parser')
    estatisticas = soup.find('div', class_="statRow")
    if(estatisticas):
        primeiraEstatistica = estatisticas.find('div', class_="statText--titleValue")
        primeiraEstatistica = primeiraEstatistica.text
        if(primeiraEstatistica == 'Posse de bola'):
            return True
        else:
            
            return False

    # fotosTimes = soup.findAll('a', class_="participant-imglink")
    # for team in fotosTimes: 
    #     print(team)
    return False


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

    diferencaGolsPrimeiroTempo = int(golsMandante) - int(golsVisitante)

    #Variável
    placarAtual = None

    if(golsMandante == golsVisitante):
        placarAtual = 'E'
    elif(golsMandante > golsVisitante):
        placarAtual = 'V'
    else:
        placarAtual = 'D'

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

    return dicionario

modelo = ""

def maquina():

    dataset = pd.read_csv('dadosFirstTime.csv', low_memory=False)
    dataset.drop(['País', 'Campeonato', 'timeMandante', 'timeVisitante', 'FaltasM', 'FaltasV', 'Chutes bloqueadosM',
    'Chutes bloqueadosV'], axis=1, inplace=True)

    X = dataset

    novos_titulos = {
    'DesarmesM' : 'desarmes_mandante',
    'DesarmesV' : 'desarmes_visitante', 
    'Total de passesM' : 'total_passes_mandante',
    'Total de passesV' : 'total_passes_visitante',
    'AtaquesV' : 'ataques_visitante',
    'AtaquesM' : 'ataques_mandante',      
    'Ataques PerigososV' : 'ataques_perigosos_visitante',   
    'Ataques PerigososM' : 'ataques_perigosos_mandante',   
    'Chutes bloqueadosV' : 'chutes_bloqueados_visitante',    
    'Chutes bloqueadosM' : 'chutes_bloqueados_mandante',    
    'Faltas cobradasV' : 'faltas_cobradas_visitante',      
    'Faltas cobradasM': 'faltas_cobradas_mandante',     
    'Posse de bolaM' : 'posse_bola_mandante',       
    'Posse de bolaV' : 'posse_bola_visitante',      
    'ImpedimentosM'  : 'impedimentos_mandante',    
    'ImpedimentosV'  : 'impedimentos_visitante',        
    'Chutes foraV' : 'chutes_fora_visitante',          
    'Chutes foraM' : 'chutes_fora_mandante',         
    'EscanteiosM' : 'escanteios_mandante',           
    'EscanteiosV' : 'escanteios_visitante',            
    'Defesas do goleiroV' : 'defesas_goleiro_visitante',     
    'Defesas do goleiroM' : 'defesas_goleiro_mandante',    
    'Tentativas de golV'  : 'tentativas_gol_visitante',    
    'Tentativas de golM'  : 'tentativas_gol_mandante',    
    'FinalizaçõesV'  : 'finalizacoes_visitante',         
    'FinalizaçõesM'  : 'finalizacoes_mandante',        
    'DiferencaGols'  : 'diferenca_gols_primeiro_tempo',           
    'Cartões amarelosM' : 'cartoes_amarelos_mandante',     
    'Cartões amarelosV' : 'cartoes_amarelos_visitante',        
    'Cartões VermelhosM': 'cartoes_vermelhos_mandante',       
    'Cartões VermelhosV': 'cartoes_vermelhos_visitante',       
    'OddM': 'odd_mandante',                      
    'OddE': 'odd_empate',                     
    'OddV': 'odd_visitante',                      
    'PlacarPrimeiroTempo': 'placar_primeiro_tempo',
}

    X = X.rename(columns=novos_titulos)

    mediana_posse_bola_mandante = X.posse_bola_mandante.median()
    mediana_posse_bola_visitante = X.posse_bola_visitante.median()


    mediana_tentativas_gol_mandante = X.tentativas_gol_mandante.median()
    mediana_tentativas_gol_visitante = X.tentativas_gol_visitante.median()

    mediana_finalizacoes_mandante = X.finalizacoes_mandante.median()
    mediana_finalizacoes_visitante = X.finalizacoes_visitante.median()

    mediana_chutes_fora_mandante = X.chutes_fora_mandante.median()
    mediana_chutes_fora_visitante = X.chutes_fora_visitante.median()

    mediana_faltas_cobradas_mandante = X.faltas_cobradas_mandante.median()
    mediana_faltas_cobradas_visitante = X.faltas_cobradas_visitante.median()

    mediana_escanteios_mandante = X.escanteios_mandante.median()
    mediana_escanteios_visitante = X.escanteios_visitante.median()

    mediana_impedimentos_mandante = X.impedimentos_mandante.median()
    mediana_impedimentos_visitante = X.impedimentos_visitante.median()

    mediana_defesas_goleiro_mandante = X.defesas_goleiro_mandante.median()
    mediana_defesas_goleiro_visitante = X.defesas_goleiro_visitante.median()

    ########

    mediana_desarmes_mandante = X.desarmes_mandante.median()
    mediana_desarmes_visitante = X.desarmes_visitante.median()

    mediana_total_passes_mandante = X.total_passes_mandante.median()
    mediana_total_passes_visitante = X.total_passes_visitante.median()

    mediana_ataques_mandante = X.ataques_mandante.median()
    mediana_ataques_visitante = X.ataques_visitante.median()

    mediana_ataques_perigosos_mandante = X.ataques_perigosos_mandante.median()
    mediana_ataques_perigosos_visitante = X.ataques_perigosos_visitante.median()

    X.posse_bola_mandante.fillna(mediana_posse_bola_mandante, inplace=True)
    X.posse_bola_visitante.fillna(mediana_posse_bola_visitante,inplace=True)

    X.tentativas_gol_mandante.fillna(mediana_tentativas_gol_mandante,inplace=True)
    X.tentativas_gol_visitante.fillna(mediana_tentativas_gol_visitante,inplace=True)

    X.finalizacoes_mandante.fillna(mediana_finalizacoes_mandante,inplace=True)
    X.finalizacoes_visitante.fillna(mediana_finalizacoes_visitante,inplace=True)

    X.chutes_fora_mandante.fillna(mediana_chutes_fora_mandante,inplace=True)
    X.chutes_fora_visitante.fillna(mediana_chutes_fora_visitante,inplace=True)

    X.faltas_cobradas_mandante.fillna(mediana_faltas_cobradas_mandante,inplace=True)
    X.faltas_cobradas_visitante.fillna(mediana_faltas_cobradas_visitante,inplace=True)

    X.escanteios_mandante.fillna(mediana_escanteios_mandante,inplace=True)
    X.escanteios_visitante.fillna(mediana_escanteios_visitante,inplace=True)

    X.impedimentos_mandante.fillna(mediana_impedimentos_mandante,inplace=True)
    X.impedimentos_visitante.fillna(mediana_impedimentos_visitante,inplace=True)

    X.defesas_goleiro_mandante.fillna(mediana_defesas_goleiro_mandante,inplace=True)
    X.defesas_goleiro_visitante.fillna(mediana_defesas_goleiro_visitante,inplace=True)

    ########

    X.desarmes_mandante.fillna(mediana_desarmes_mandante,inplace=True)
    X.desarmes_visitante.fillna(mediana_desarmes_visitante,inplace=True)

    X.total_passes_mandante.fillna(mediana_total_passes_mandante,inplace=True)
    X.total_passes_visitante.fillna(mediana_total_passes_visitante,inplace=True)

    X.ataques_mandante.fillna(mediana_ataques_mandante,inplace=True)
    X.ataques_visitante.fillna(mediana_ataques_visitante,inplace=True)

    X.ataques_perigosos_mandante.fillna(mediana_ataques_perigosos_mandante,inplace=True)
    X.ataques_perigosos_visitante.fillna(mediana_ataques_perigosos_visitante,inplace=True)

    remove_posse =  X.loc[X['posse_bola_mandante'] == 0]
    X.drop(remove_posse.index, inplace=True)

    X['posse_bola'] = 0
    X['tentativas_gol'] = 0
    X['finalizacoes'] = 0
    X['chutes_fora'] = 0
    X['faltas_cobradas'] = 0
    X['escanteios'] = 0
    X['impedimentos'] = 0
    X['defesas_goleiro'] = 0
    X['cartoes_amarelos'] = 0
    X['cartoes_vermelhos'] = 0

    X['desarmes'] = 0
    X['total_passes'] = 0
    X['ataques'] = 0
    X['ataques_perigosos'] = 0

    for idx, _ in X.iterrows():
        X['posse_bola'].at[idx] = X['posse_bola_mandante'].at[idx] - X['posse_bola_visitante'].at[idx]
        X['tentativas_gol'].at[idx] = X['tentativas_gol_mandante'].at[idx] - X['tentativas_gol_visitante'].at[idx]
        X['finalizacoes'].at[idx] = X['finalizacoes_mandante'].at[idx] - X['finalizacoes_visitante'].at[idx]
        X['chutes_fora'].at[idx] = X['chutes_fora_mandante'].at[idx] - X['chutes_fora_visitante'].at[idx]
        X['faltas_cobradas'].at[idx] = X['faltas_cobradas_mandante'].at[idx] - X['faltas_cobradas_visitante'].at[idx]
        X['escanteios'].at[idx] = X['escanteios_mandante'].at[idx] - X['escanteios_visitante'].at[idx]
        X['impedimentos'].at[idx] = X['impedimentos_mandante'].at[idx] - X['impedimentos_visitante'].at[idx]
        X['defesas_goleiro'].at[idx] = X['defesas_goleiro_mandante'].at[idx] - X['defesas_goleiro_visitante'].at[idx]
        X['cartoes_amarelos'].at[idx] = X['cartoes_amarelos_mandante'].at[idx] - X['cartoes_amarelos_visitante'].at[idx]
        X['cartoes_vermelhos'].at[idx] = X['cartoes_vermelhos_mandante'].at[idx] - X['cartoes_vermelhos_visitante'].at[idx]
        
        X['desarmes'].at[idx] = X['desarmes_mandante'].at[idx] - X['desarmes_visitante'].at[idx]
        X['total_passes'].at[idx] = X['total_passes_mandante'].at[idx] - X['total_passes_visitante'].at[idx]
        X['ataques'].at[idx] = X['ataques_mandante'].at[idx] - X['ataques_visitante'].at[idx]
        X['ataques_perigosos'].at[idx] = X['ataques_perigosos_mandante'].at[idx] - X['ataques_perigosos_visitante'].at[idx]

    X.drop(['posse_bola_mandante', 'posse_bola_visitante', 'tentativas_gol_mandante', 'tentativas_gol_visitante',
       'finalizacoes_mandante', 'finalizacoes_visitante', 'chutes_fora_mandante', 'chutes_fora_visitante',
       'faltas_cobradas_mandante', 'faltas_cobradas_visitante', 'escanteios_mandante', 'escanteios_visitante',
       'impedimentos_mandante', 'impedimentos_visitante', 'defesas_goleiro_mandante', 'defesas_goleiro_visitante',
       'cartoes_amarelos_mandante', 'cartoes_amarelos_visitante', 'cartoes_vermelhos_mandante', 'cartoes_vermelhos_visitante',
       'desarmes_mandante', 'desarmes_visitante', 'total_passes_mandante', 'total_passes_visitante', 
        'ataques_mandante', 'ataques_visitante', 'ataques_perigosos_mandante', 'ataques_perigosos_visitante'
       
       ], axis=1, inplace=True)

    X = pd.get_dummies(X, columns=['placar_primeiro_tempo'])

    y = X.PlacarFinal
    X = X.drop('PlacarFinal', axis=1)

    X.drop(['total_passes', 'defesas_goleiro', 'ataques', 'ataques_perigosos', 'cartoes_amarelos',
        'faltas_cobradas', 'tentativas_gol', 'desarmes'
        , 'odd_visitante', 'odd_empate'
       ], axis=1, inplace=True)

    from imblearn.under_sampling import NearMiss
    nr = NearMiss()
    X, y = nr.fit_sample(X, y)

    from sklearn.model_selection import train_test_split
    from sklearn import linear_model
    lm = linear_model.LinearRegression()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=123)

    from sklearn.linear_model import LogisticRegression
    global modelo
    modelo = LogisticRegression(random_state=123, max_iter=1000).fit(X_train, y_train)
    modelo.fit(X_train, y_train)

    return modelo

def predizer(dicionario):

    # dicionario = {'Posse de bola': ['60', '40'], 'Tentativas de gol': ['3', '1'], 'Finalizações': ['2', '1'], 'Chutes fora': ['1', '0'], 
    # 'Escanteios': ['1', '0'], 'Impedimentos': ['0', '3'], 'Defesas do goleiro': ['1', '2'], 'Faltas': ['2', '5'], 'Ataques': ['37', '28'], 
    # 'Ataques Perigosos': ['26', '13'], 'Cartões vermelhos': ['0', '0'], 'oddCasa': '2.10', 'oddEmpate': '2.87', 'oddVisitante': '4.00', 'diferencaGols': 0}

    oddMandante = float(dicionario['oddCasa'])
    oddEmpate = float(dicionario['oddEmpate'])
    oddVisitante = float(dicionario['oddVisitante'])

    diferencaGols = int(dicionario['diferencaGols'])
    if(diferencaGols == 0):
        placarPrimeiroTempoD  = 0
        placarPrimeiroTempoV = 0
        placarPrimeiroTempoE = 1
    elif(diferencaGols > 1):
        placarPrimeiroTempoD  = 0
        placarPrimeiroTempoV = 1
        placarPrimeiroTempoE = 0
    else:
        placarPrimeiroTempoD  = 1
        placarPrimeiroTempoV = 0
        placarPrimeiroTempoE = 0

    posseBola = int(dicionario['Posse de bola'][0]) - int(dicionario['Posse de bola'][1])
    finalizacoes = int(dicionario['Finalizações'][0]) - int(dicionario['Finalizações'][1])
    chutesFora = int(dicionario['Chutes fora'][0]) - int(dicionario['Chutes fora'][1])
    escanteios = int(dicionario['Escanteios'][0]) - int(dicionario['Escanteios'][1])
    impedimentos = int(dicionario['Impedimentos'][0]) - int(dicionario['Impedimentos'][1])
    cartoesVermelhos = int(dicionario['Cartões vermelhos'][0]) - int(dicionario['Cartões vermelhos'][1])

    atributos = [[oddMandante, diferencaGols, posseBola, finalizacoes,
    chutesFora, escanteios, impedimentos, cartoesVermelhos, placarPrimeiroTempoD, placarPrimeiroTempoE, placarPrimeiroTempoV]]

    dataset = pd.DataFrame(atributos,columns=['odd_mandante', 'diferenca_gols_primeiro_tempo' ,'posse_bola', 
    'finalizacoes','chutes_fora', 'escanteios', 'impedimentos', 'cartoes_vermelhos', 'placar_primeiro_tempo_D', 'placar_primeiro_tempo_E',
    'placar_primeiro_tempo_V'])

    # dataset['posse_bola'].at[0] = int(dicionario['Posse de bola'][0]) - int(dicionario['Posse de bola'][1])
    # dataset['finalizacoes'].at[0] = int(dicionario['Finalizações'][0]) - int(dicionario['Finalizações'][1])
    # dataset['chutes_fora'].at[0] = int(dicionario['Chutes fora'][0]) - int(dicionario['Chutes fora'][1])
    # dataset['escanteios'].at[0] = int(dicionario['Escanteios'][0]) - int(dicionario['Escanteios'][1])
    # dataset['impedimentos'].at[0] = int(dicionario['Impedimentos'][0]) - int(dicionario['Impedimentos'][1])
    # dataset['cartoes_vermelhos'].at[0] = int(dicionario['Cartões vermelhos'][0]) - int(dicionario['Cartões vermelhos'][1])

    y_pred = modelo.predict(dataset)
    probabilidades = modelo.predict_proba(dataset)
    probabilidadeDerrota = probabilidades[0][0]
    probabilidadeEmpate = probabilidades[0][1]
    probabilidadeVitoria = probabilidades[0][2]
    
    return [y_pred[0], probabilidadeDerrota, probabilidadeEmpate, probabilidadeVitoria]