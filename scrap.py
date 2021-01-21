import pandas as pd
import numpy as np
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import config
import time
from utils.dados import formata_num_colecao, carrega_dados, checa_colecao
from utils.scraper import carrega_driver, busca_nome, carrega_todas_colecoes, procura_colecao, seleciona_colecao

df = carrega_dados(config=config)
#driver = carrega_driver(config=config, headless=True)
df = pd.DataFrame(data=[['Charizard', ('4/102'), 'foil', 'EN', 'NM']], columns=['nome', 'num_colecao', 'extras', 'lingua', 'condicao'])
df.num_colecao = df.num_colecao.map(formata_num_colecao) #testes
driver = carrega_driver(config=config, headless=False) #testes

timeout = 10
result_pokemon = list()
for idx, row in df.iterrows(): #busca cada 'nome' em df
    #--------------Inicia primeira busca pelo nome----------------------
    print('Procurando todos os {}'.format(row['nome']))
    busca_nome(driver=driver, nome=row['nome'], timeout=timeout)
    # ------------------------------------------------------------------

    # -------------Loop para carregar todos na página ("Exibir mais")---------
    timeout = 3
    carrega_todas_colecoes(driver=driver, timeout=timeout)
    # ------------------------------------------------------------------

    #--------------Procura dentre as coleções que apareceram no site----------
    colecao, codigo_colecao = procura_colecao(driver, row['num_colecao'])
    # -----------------------------------------------------------------------

    if colecao: #caso tenha encontrado alguma igual ao df
        timeout = 5
        seleciona_colecao(colecao=colecao, driver=driver, timeout=timeout)
        linhas = driver.find_elements_by_class_name('estoque-linha.ecom-marketplace')
        for linha in linhas:
            qualidade_card = linha.find_element_by_class_name('e-col4').text
            lingua_card = None
            for lingua in ['Inglês', 'Português', 'Português / Inglês']: #procura a lingua do card
                try:
                    innerHTML = linha.find_element_by_class_name('e-col4').get_attribute('innerHTML')
                    if lingua in innerHTML:
                        lingua_card = lingua
                    '''
                    lingua_card = linha.find_element_by_class_name('e-col4').find_element_by_xpath(
                        '//img[@title="{}"]'.format(lingua)).get_attribute("title")
                    '''
                except NoSuchElementException:
                    pass
            try:
                extras = linha.find_element_by_class_name('e-mob-extranw').text
            except NoSuchElementException:
                extras = None

            possiveis_precos = []
            possiveis_precos.append(linha.find_element_by_class_name('e-col3').get_attribute('textContent'))
            possiveis_precos.append(linha.find_element_by_class_name('e-col3').get_attribute('innerText'))
            possiveis_precos.append(linha.find_element_by_class_name('e-col9-mobile').get_attribute('innerText'))
            possiveis_precos.append(linha.find_element_by_class_name('e-col9-mobile').text)
            possiveis_precos_float = []
            for preco_possivel in possiveis_precos:
                try:
                    possiveis_precos_float.append(
                    float(preco_possivel.split('R$ ')[-1].replace('.','').replace(',', '.')))
                except ValueError:
                    print(preco_possivel)
            possiveis_precos_float = list(np.unique(possiveis_precos_float))
            print(possiveis_precos_float)
            result_pokemon.append((row['nome'], codigo_colecao, qualidade_card, lingua_card, extras, possiveis_precos_float))
    else:
        print('Não foi encontrada esta coleção')