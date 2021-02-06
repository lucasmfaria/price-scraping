import time
import numpy as np
from pathlib import Path
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, StaleElementReferenceException, TimeoutException
from utils.dados import checa_colecao, extrai_preco_string, constroi_resultados

class LigaPokemonScraper:
    def __init__(self, correcoes_num_colecao, website='https://www.ligapokemon.com.br/', timeout_busca_principal=10,
                 timeout_exibir_mais=8, timeout_seleciona_card=8, timeout_botao_carrinho=4,
                 espera_botao_comprar=1, n_max_tentativas_preco=16, n_max_tentativas_colecao=3,
                 debug=False):
        self.website = website
        self.timeout_busca_principal = timeout_busca_principal
        self.timeout_exibir_mais = timeout_exibir_mais
        self.timeout_seleciona_card = timeout_seleciona_card
        self.timeout_botao_carrinho = timeout_botao_carrinho
        self.espera_botao_comprar = espera_botao_comprar
        self.n_max_tentativas_preco = n_max_tentativas_preco
        self.n_max_tentativas_colecao = n_max_tentativas_colecao
        self.debug = debug
        self.correcoes_num_colecao = correcoes_num_colecao
        self.carrega_driver()

    def carrega_driver(self):
        if self.debug == False:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            self.driver = webdriver.Chrome(options=chrome_options)
        elif self.debug == True:
            self.driver = webdriver.Chrome()
        self.driver.get(self.website)

    def busca_nome(self, nome):
        elem = self.driver.find_element_by_id("mainsearch")
        elem.clear()
        elem.send_keys(nome)
        elem.send_keys(Keys.RETURN)
        try:
            element_present = EC.presence_of_element_located((By.CLASS_NAME, 'mtg-single'))
            WebDriverWait(self.driver, self.timeout_busca_principal).until(element_present)
        except TimeoutException:
            print('TIMEOUT')

    def clica_exibir_mais(self):
        try:
            while True:
                self.driver.find_element_by_class_name('exibir-mais').click()
                element_present = EC.element_to_be_clickable((By.CLASS_NAME, 'exibir-mais'))
                WebDriverWait(self.driver, self.timeout_exibir_mais).until(element_present)
        except ElementNotInteractableException:
            pass
        except NoSuchElementException:
            pass
        except TimeoutException:
            pass

    def procura_colecao(self, num_colecao_df):
        colecoes = self.driver.find_elements_by_class_name('mtg-single')
        colecao_encontrada = None
        idx_colecao = None
        codigo_colecao_encontrada = None
        for idx, colecao in enumerate(colecoes):
            if len(colecao.find_elements_by_class_name('mtg-numeric-code')) > 0:
                codigo_colecao = colecao.find_elements_by_class_name('mtg-numeric-code')[0].text
                if checa_colecao(codigo_colecao, num_colecao_df):  # caso tenha encontrado o card em questão
                    idx_colecao = idx
                    break

        if idx_colecao == None:  # busca denovo com as correções de identificador de coleção
            for idx, colecao in enumerate(colecoes):
                if len(colecao.find_elements_by_class_name('mtg-numeric-code')) > 0:
                    codigo_colecao = colecao.find_elements_by_class_name('mtg-numeric-code')[0].text
                    try:
                        num_colecao_df_corrigido = (
                        num_colecao_df[0], self.correcoes_num_colecao[num_colecao_df[1]])
                        if checa_colecao(codigo_colecao,
                                         num_colecao_df_corrigido):  # caso tenha encontrado o card em questão
                            idx_colecao = idx
                            break
                    except KeyError:
                        pass

        if idx_colecao != None:
            colecao_encontrada = colecoes[idx_colecao]
            codigo_colecao_encontrada = num_colecao_df
        return colecao_encontrada, codigo_colecao_encontrada

    def busca_card(self, nome, num_colecao):
        n_tentativas_colecao = 0
        colecao = None
        codigo_colecao = None
        while (colecao == None) and (n_tentativas_colecao <= self.n_max_tentativas_colecao):
            self.busca_nome(nome)
            self.clica_exibir_mais()
            colecao, codigo_colecao = self.procura_colecao(num_colecao)
            n_tentativas_colecao = n_tentativas_colecao + 1
        return colecao, codigo_colecao

    def busca(self, nome, num_colecao, precos_list, preco_acumulado, df_precos_parcial, df_cards, estatistica, csv_input_path):
        precos_list_copy = precos_list.copy()
        preco_acumulado_novo = preco_acumulado
        colecao, codigo_colecao = self.busca_card(nome, num_colecao)
        if colecao:
            self.seleciona_colecao(colecao)
            self.clica_exibir_mais()
            linhas = self.encontra_linhas()
            for linha in linhas:
                qualidade_card = self.encontra_qualidade(linha)
                lingua_card = self.encontra_lingua(linha)
                extras = self.encontra_extras(linha)
                self.aperta_comprar(linha)
                preco_unitario = self.encontra_preco(preco_acumulado_novo)

                if preco_unitario == 0:
                    preco_unitario = np.nan
                else:
                    preco_acumulado_novo = preco_acumulado_novo + preco_unitario

                card_info = (
                    nome, codigo_colecao, extras, lingua_card, qualidade_card,
                    preco_unitario)
                print((card_info[:-1]) + (
                    round(card_info[-1],
                          2),))  # print na tela arredondando o último valor ("preco_unitario")
                precos_list_copy.append(card_info)
            constroi_resultados(precos_list_copy, df_precos_parcial, df_cards, estatistica,
                                Path(csv_input_path))
        else:
            print('Não foi encontrada esta coleção')

        return precos_list_copy, preco_acumulado_novo

    def seleciona_colecao(self, colecao):
        try:
            while True:
                colecao.click()
                time.sleep(1)
                colecao.click()
                element_present = EC.presence_of_element_located(
                    (By.CLASS_NAME, 'estoque-linha.ecom-marketplace'))
                WebDriverWait(self.driver, self.timeout_seleciona_card).until(element_present)
        except ElementNotInteractableException:
            pass
        except NoSuchElementException:
            pass
        except TimeoutException:
            pass
        except StaleElementReferenceException:
            try:
                element_present = EC.presence_of_element_located(
                    (By.CLASS_NAME, 'estoque-linha.ecom-marketplace'))
                WebDriverWait(self.driver, self.timeout_seleciona_card).until(element_present)
            except TimeoutException:
                pass
                # TODO - tratar exception

    def encontra_linhas(self):
        return self.driver.find_elements_by_class_name('estoque-linha.ecom-marketplace')

    def encontra_qualidade(self, linha):
        return linha.find_element_by_class_name('e-col4').text

    def encontra_lingua(self, linha):
        lingua_card = ''
        try:
            innerHTML = linha.find_element_by_class_name('e-col4').get_attribute('innerHTML')
            lingua_card = innerHTML[innerHTML.index('title="') + len('title="'):innerHTML.index('" style')]
        except NoSuchElementException:
            pass
        return lingua_card

    def encontra_extras(self, linha):
        try:
            extras = linha.find_element_by_class_name('e-mob-extranw').get_attribute('innerHTML')
        except NoSuchElementException:
            extras = ''
        return extras

    def aperta_comprar(self, linha):
        botao_comprar = linha.find_element_by_class_name('buy')
        botao_comprar.click()
        time.sleep(self.espera_botao_comprar)

    def busca_preco(self, preco_acumulado):
        botao_carrinho = self.driver.find_element_by_id('dropdownMenuCart')
        botao_carrinho.click()
        try:
            element_present = EC.visibility_of_element_located(
                (By.CLASS_NAME, 'header-cart-sum'))
            WebDriverWait(self.driver, self.timeout_botao_carrinho).until(element_present)
        except TimeoutException:
            print('--------------Timeout na espera da soma do carrinho----------------')
            return 0.0

        preco_total = self.driver.find_element_by_class_name('header-cart-sum').find_element_by_class_name(
            'price').get_attribute('innerHTML')
        preco_total = extrai_preco_string(preco_total)
        preco_unitario = preco_total - preco_acumulado
        return preco_unitario

    def encontra_preco(self, preco_acumulado):
        preco_unitario = self.busca_preco(preco_acumulado)
        n_tentativas_preco = 0
        while (preco_unitario == 0) and (n_tentativas_preco <= self.n_max_tentativas_preco):
            print('preco_unitario = {}, tentando coletar preço novamente'.format(preco_unitario))
            preco_unitario = self.busca_preco(preco_acumulado)
            n_tentativas_preco = n_tentativas_preco + 1
        return preco_unitario

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
