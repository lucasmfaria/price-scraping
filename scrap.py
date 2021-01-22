import pandas as pd
from selenium.common.exceptions import NoSuchElementException
import config
from utils.dados import carrega_dados, salva_dados, formata_num_colecao
from utils.scraper import carrega_driver, busca_nome, clica_exibir_mais, procura_colecao, seleciona_colecao, retorna_lingua_card, retorna_preco

df = carrega_dados(config=config)
if config.DEBUG:
    df = pd.DataFrame(data=[['Charizard', ('4/102'), 'foil', 'EN', 'NM']], columns=['nome', 'num_colecao', 'extras', 'lingua', 'condicao']) #testes
    #df = pd.DataFrame(data=[['Mew', ('19/165'), 'foil', 'EN', 'NM']], columns=['nome', 'num_colecao', 'extras', 'lingua', 'condicao']) #testes
    df.num_colecao = df.num_colecao.map(formata_num_colecao) #testes
    driver = carrega_driver(config=config, headless=False) #testes
else:
    driver = carrega_driver(config=config, headless=True)

result_pokemon_website_1 = list()
preco_acumulado = 0
cards_ja_buscados = set() #rastreia os cards das coleções já buscadas para não duplicar
for idx, row in df.iterrows(): #busca cada 'nome' em df
    if (row['nome'], row['num_colecao']) not in cards_ja_buscados:
        cards_ja_buscados.add((row['nome'], row['num_colecao']))

        #--------------Inicia primeira busca pelo nome----------------------------
        print('Procurando todos os {} coleção {}'.format(row['nome'], row['num_colecao']))
        busca_nome(driver=driver, nome=row['nome'], timeout=config.TIMEOUT_BUSCA_PRINCIPAL)
        # ------------------------------------------------------------------------
        # -------------Loop para carregar todos na página ("Exibir mais")---------
        clica_exibir_mais(driver=driver, timeout=config.TIMEOUT_EXIBIR_MAIS)
        # ------------------------------------------------------------------------
        #--------------Procura dentre as coleções que apareceram no site----------
        colecao, codigo_colecao = procura_colecao(driver, row['num_colecao'])
        # ------------------------------------------------------------------------

        if colecao: #caso tenha encontrado alguma igual ao df
            seleciona_colecao(colecao=colecao, driver=driver, timeout=config.TIMEOUT_SELECIONA_CARD)
            clica_exibir_mais(driver=driver, timeout=config.TIMEOUT_EXIBIR_MAIS)

            linhas = driver.find_elements_by_class_name('estoque-linha.ecom-marketplace')
            for linha in linhas:
                qualidade_card = linha.find_element_by_class_name('e-col4').text
                lingua_card = retorna_lingua_card(linha=linha, config=config)
                try:
                    extras = linha.find_element_by_class_name('e-mob-extranw').text
                except NoSuchElementException:
                    extras = None

                preco = retorna_preco(driver, linha, preco_acumulado, timeout=config.TIMEOUT_BOTAO_COMPRA)
                preco_acumulado = preco_acumulado + preco

                card_info = (row['nome'], codigo_colecao, extras, lingua_card, qualidade_card, round(preco, 2))
                print(card_info)
                result_pokemon_website_1.append(card_info)
                df_result = pd.DataFrame(result_pokemon_website_1, columns=df.columns.append(pd.Index(['preco'])))
                salva_dados(df=df_result, nome_arquivo=config.CSV_OUTPUT_TODOS)
                salva_dados(df=df.applymap(lambda x: x.lower() if type(x) == str else x).merge(df_result.applymap(lambda x: x.lower() if type(x) == str else x), how='left', on=['nome', 'num_colecao', 'extras', 'lingua', 'condicao']), nome_arquivo=config.CSV_OUTPUT_MERGE)
        else:
            print('Não foi encontrada esta coleção')