import pandas as pd
import numpy as np
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import config
import time
from utils.dados import formata_num_colecao, carrega_dados
from utils.scraper import carrega_driver, busca_nome, carrega_todas_colecoes

df = carrega_dados(config=config)
#driver = carrega_driver(config=config, headless=True)
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

    pokemons = driver.find_elements_by_class_name('mtg-single')
    for pokemon in pokemons:
        if len(pokemon.find_elements_by_class_name('mtg-numeric-code')) > 0:
            codigo_colecao = pokemon.find_elements_by_class_name('mtg-numeric-code')[0].text
            codigo_colecao = codigo_colecao.split('(')[-1].split(')')[0]
            codigo_colecao = formata_num_colecao(codigo_colecao)
            if codigo_colecao == row['num_colecao']: #caso tenha encontrado o pokemon em questão
                pokemon.click()
                time.sleep(1)
                try:
                    pokemon.click()
                    time.sleep(3)
                except StaleElementReferenceException:
                    pass
                linhas = driver.find_elements_by_class_name('estoque-linha.ecom-marketplace.estoque-linha-extras')
                for linha in linhas:
                    qualidade_card = linha.find_element_by_class_name('e-col4').text
                    lingua_card = None
                    for lingua in ['Inglês', 'Português', 'Português / Inglês']: #procura a lingua do card
                        try:
                            lingua_card = linha.find_element_by_class_name('e-col4').find_element_by_xpath(
                                '//*[@title="{}"]'.format(lingua)).get_attribute("title")
                        except NoSuchElementException:
                            pass
                        else:
                            break
                    extras = linha.find_element_by_class_name('e-mob-extranw').text

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
                break
