import pandas as pd
import numpy as np
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import config
import time
from utils.dados import formata_num_colecao, carrega_dados, checa_colecao
from utils.scraper import carrega_driver, busca_nome, clica_exibir_mais, procura_colecao, seleciona_colecao, retorna_lingua_card, retorna_preco

df = carrega_dados(config=config)
#driver = carrega_driver(config=config, headless=True)
#df = pd.DataFrame(data=[['Charizard', ('4/102'), 'foil', 'EN', 'NM']], columns=['nome', 'num_colecao', 'extras', 'lingua', 'condicao'])
#df = pd.DataFrame(data=[['Mew', ('19/165'), 'foil', 'EN', 'NM']], columns=['nome', 'num_colecao', 'extras', 'lingua', 'condicao'])
#df.num_colecao = df.num_colecao.map(formata_num_colecao) #testes
driver = carrega_driver(config=config, headless=False) #testes

timeout = 10
result_pokemon = list()
preco_acumulado = 0
for idx, row in df.iterrows(): #busca cada 'nome' em df
    #--------------Inicia primeira busca pelo nome----------------------
    print('Procurando todos os {}'.format(row['nome']))
    busca_nome(driver=driver, nome=row['nome'], timeout=timeout)
    # ------------------------------------------------------------------

    # -------------Loop para carregar todos na página ("Exibir mais")---------
    timeout = 3
    clica_exibir_mais(driver=driver, timeout=timeout)
    # ------------------------------------------------------------------

    #--------------Procura dentre as coleções que apareceram no site----------
    colecao, codigo_colecao = procura_colecao(driver, row['num_colecao'])
    # -----------------------------------------------------------------------

    if colecao: #caso tenha encontrado alguma igual ao df
        timeout = 5
        seleciona_colecao(colecao=colecao, driver=driver, timeout=timeout)

        timeout = 3
        clica_exibir_mais(driver=driver, timeout=timeout)

        linhas = driver.find_elements_by_class_name('estoque-linha.ecom-marketplace')
        for linha in linhas:
            qualidade_card = linha.find_element_by_class_name('e-col4').text
            lingua_card = retorna_lingua_card(linha=linha, config=config)
            try:
                extras = linha.find_element_by_class_name('e-mob-extranw').text
            except NoSuchElementException:
                extras = None

            preco = retorna_preco(driver, linha, preco_acumulado)
            preco_acumulado = preco_acumulado + preco
            
            result_pokemon.append(
                (row['nome'], codigo_colecao, qualidade_card, lingua_card, extras, preco))
    else:
        print('Não foi encontrada esta coleção')