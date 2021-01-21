import time
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, StaleElementReferenceException, TimeoutException
from utils.dados import checa_colecao

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

def carrega_todas_colecoes(driver, timeout=5):
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
        codigo_colecao_encontrada = codigo_colecao
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
