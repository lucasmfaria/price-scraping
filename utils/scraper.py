import time
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, StaleElementReferenceException, TimeoutException
from utils.dados import checa_colecao, extrai_preco_string

def carrega_driver(config, headless=False):
    if headless == True:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
    else:
        driver = webdriver.Chrome()
    driver.get(config.WEBSITE_1)
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
    if idx_colecao:
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

def retorna_lingua_card(linha, config):
    lingua_card = None
    for lingua in config.LINGUAS_POSSIVEIS:  # procura a lingua do card
        try:
            innerHTML = linha.find_element_by_class_name('e-col4').get_attribute('innerHTML')
            if lingua in innerHTML:
                lingua_card = lingua
        except NoSuchElementException:
            pass
    return lingua_card

def retorna_preco(driver, linha, preco_acumulado, timeout=5):
    botao_comprar = linha.find_element_by_class_name('buy')
    botao_comprar.click()
    time.sleep(2)

    botao_carrinho = driver.find_element_by_id('dropdownMenuCart')
    botao_carrinho.click()
    time.sleep(2)
    '''
    element_present = EC.visibility_of_element_located(
        (By.CLASS_NAME, 'header-cart-sum'))
    WebDriverWait(driver, timeout).until(element_present)
    '''
    preco_total = driver.find_element_by_class_name('header-cart-sum').find_element_by_class_name('price').text
    preco_total = extrai_preco_string(preco_total)
    preco = preco_total - preco_acumulado

    return preco
