import pandas as pd
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException
import config
import time
from utils.dados import formata_num_colecao

df = pd.read_csv(Path('./data') / config.CSV_NAME, sep=';')
df.num_colecao = df.num_colecao.map(formata_num_colecao)

driver = webdriver.Chrome()
driver.get("https://www.ligapokemon.com.br/")

for nome in df.nome:
    print('Procurando todos os {}'.format(nome))
    elem = driver.find_element_by_id("mainsearch")
    elem.clear()
    elem.send_keys(nome)
    elem.send_keys(Keys.RETURN)
    try:
        while True:
            driver.find_element_by_class_name('exibir-mais').click()
            time.sleep(3)
            print('Encontrado um botão "Exibir mais cards"')
    except ElementNotInteractableException:
        print('Quantidade total de {} encontrados'.format(nome))
    except NoSuchElementException:
        pass
    print('Procurando cada {}'.format(nome))
    pokemons = driver.find_elements_by_class_name('mtg-single')
    for pokemon in pokemons:
        if len(pokemon.find_elements_by_class_name('mtg-numeric-code')) > 0:
            codigo_colecao = pokemon.find_elements_by_class_name('mtg-numeric-code')[0].text
            codigo_colecao = codigo_colecao.split('(')[-1].split(')')[0]
            codigo_colecao = formata_num_colecao(codigo_colecao)

        print(codigo_colecao)
