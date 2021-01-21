from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException

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

