import time
import numpy as np
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, StaleElementReferenceException, TimeoutException
from utils.dados import checa_colecao, extrai_preco_string

def carrega_driver(website, headless=False):
    if headless == True:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
    else:
        driver = webdriver.Chrome()
    driver.get(website)
    return driver

def busca_nome(driver, nome, timeout=10):
    elem = driver.find_element_by_id("mainsearch")
    elem.clear()
    elem.send_keys(nome)
    elem.send_keys(Keys.RETURN)
    try:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'mtg-single'))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        print('TIMEOUT')

def clica_exibir_mais(driver, timeout=5):
    try:
        while True:
            driver.find_element_by_class_name('exibir-mais').click()
            element_present = EC.element_to_be_clickable((By.CLASS_NAME, 'exibir-mais'))
            WebDriverWait(driver, timeout).until(element_present)
    except ElementNotInteractableException:
        pass
    except NoSuchElementException:
        pass
    except TimeoutException:
        pass

def procura_colecao(driver, num_colecao_df):
    colecoes = driver.find_elements_by_class_name('mtg-single')
    colecao_encontrada = None
    idx_colecao = None
    codigo_colecao_encontrada = None
    for idx, colecao in enumerate(colecoes):
        if len(colecao.find_elements_by_class_name('mtg-numeric-code')) > 0:
            codigo_colecao = colecao.find_elements_by_class_name('mtg-numeric-code')[0].text
            if checa_colecao(codigo_colecao, num_colecao_df):  # caso tenha encontrado o card em questão
                idx_colecao = idx
                break
    if idx_colecao != None:
        colecao_encontrada = colecoes[idx_colecao]
        codigo_colecao_encontrada = num_colecao_df
    return colecao_encontrada, codigo_colecao_encontrada

def seleciona_colecao(colecao, driver, timeout=5):
    try:
        while True:
            colecao.click()
            time.sleep(1)
            colecao.click()
            element_present = EC.presence_of_element_located(
                (By.CLASS_NAME, 'estoque-linha.ecom-marketplace'))
            WebDriverWait(driver, timeout).until(element_present)
    except ElementNotInteractableException:
        pass
    except NoSuchElementException:
        pass
    except TimeoutException:
        pass
    except StaleElementReferenceException:
        element_present = EC.presence_of_element_located(
            (By.CLASS_NAME, 'estoque-linha.ecom-marketplace'))
        WebDriverWait(driver, timeout).until(element_present)
        #TODO - tratar exception

def retorna_lingua_card(linha):
    lingua_card = ''
    try:
        innerHTML = linha.find_element_by_class_name('e-col4').get_attribute('innerHTML')
        lingua_card = innerHTML[innerHTML.index('title="') + len('title="'):innerHTML.index('" style')]
    except NoSuchElementException:
        pass
    return lingua_card

def aperta_comprar(linha, espera_botao_comprar):
    botao_comprar = linha.find_element_by_class_name('buy')
    botao_comprar.click()
    time.sleep(espera_botao_comprar)

def retorna_preco_liga(driver, preco_acumulado, timeout=5):
    botao_carrinho = driver.find_element_by_id('dropdownMenuCart')
    botao_carrinho.click()
    try:
        element_present = EC.visibility_of_element_located(
            (By.CLASS_NAME, 'header-cart-sum'))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        print('--------------Timeout na espera da soma do carrinho----------------')
        return 0.0

    preco_total = driver.find_element_by_class_name('header-cart-sum').find_element_by_class_name('price').get_attribute('innerHTML')
    preco_total = extrai_preco_string(preco_total)
    preco = preco_total - preco_acumulado
    return preco

def carrega_busca_avancada(driver, config, row):
    driver.get('https://www.ebay.com/sch/ebayadvsearch')
    apenas_vendidos = driver.find_element_by_id("LH_Sold")
    if not apenas_vendidos.is_selected(): #garante que o checkbox de "Anúncios vendidos" esteja selecionado
        apenas_vendidos.click()
        time.sleep(1)
    elem = driver.find_element_by_id('_nkw')
    elem.clear()
    string_busca = row['nome'] + ' ' + str(row['num_colecao'][0]) + '/' + str(row['num_colecao'][1]) + \
                   ' ' + config.DICT_LINGUA[row['lingua'].lower()] + ' ' + config.DICT_CONDICAO[row['condicao'].lower()] + \
                   ' ' + config.DICT_EXTRAS[row['extras']]
    elem.click()
    elem.send_keys(string_busca)
    driver.find_element_by_class_name('btn.btn-prim').click()  # botão "Pesquisar"
    try:
        element_present = EC.presence_of_element_located((By.ID, 'ListViewInner'))
        WebDriverWait(driver, 10).until(element_present)
    except TimeoutException:
        print('TIMEOUT')

def retorna_preco_ebay(produto):
    string_preco = produto.find_element_by_class_name('lvprice.prc').text
    if len(string_preco.split(' ')) == 3:
        string_preco = string_preco.split(' ')[1:]
        string_preco = string_preco[0] + string_preco[1]
        preco = float(string_preco.replace('.', '').replace(',', '.'))
    else:
        preco = float(string_preco.split(' ')[-1].replace('.', '').replace(',', '.'))
    return preco

def verifica_psa(produto):
    if (' psa ' in str(produto.find_element_by_class_name('vip').get_attribute('data-mtdes')).lower()) or \
            (' psa.' in str(produto.find_element_by_class_name('vip').get_attribute('data-mtdes')).lower()) or \
            (' psa ' in str(produto.find_element_by_class_name('vip').text).lower()) or \
            (' psa.' in str(produto.find_element_by_class_name('vip').text).lower()) or \
            ('psa ' in str(produto.find_element_by_class_name('vip').text).lower()) or \
            ('psa ' in str(produto.find_element_by_class_name('vip').get_attribute('data-mtdes')).lower()):
        is_psa = True
    else:
        is_psa = False
    return is_psa

def verifica_nome(row, produto):
    for parte_nome in row['nome'].lower().split(' '):
        if len(parte_nome) > 1:
            if (parte_nome in str(produto.find_element_by_class_name('vip').get_attribute('data-mtdes')).lower()) or \
                    (parte_nome in str(produto.find_element_by_class_name('vip').text).lower()):
                is_nome = True
                break
            else:
                is_nome = False
    return is_nome