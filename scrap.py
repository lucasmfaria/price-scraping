import pandas as pd
import numpy as np
from selenium.common.exceptions import NoSuchElementException
import config
from utils.dados import carrega_dados, salva_dados, formata_num_colecao
from utils.scraper import carrega_driver, busca_nome, clica_exibir_mais, procura_colecao, seleciona_colecao, retorna_lingua_card, retorna_preco_liga, carrega_busca_avancada, retorna_preco_ebay, verifica_psa, verifica_nome, aperta_comprar
from pathlib import Path

df = carrega_dados(config=config)
df_result_aux = None
if config.CONTINUAR_DE_ONDE_PAROU:
    def formata_num_colecao_teste(num_colecao):
        split = str(num_colecao).split('(')[-1].split(')')[0].split(', ')
        if len(split) > 1:
            try:
                retorno = (int(split[0]), int(split[1]))
            except ValueError:
                retorno = (split[0], split[1])
            return retorno
        else:
            return num_colecao
    dtypes_dict = {
        'extras': str,
        'lingua': str,
        'condicao': str
    }
    df_result_aux = pd.read_csv(Path('./data') / config.CSV_OUTPUT_TODOS, sep=';', dtype=dtypes_dict, index_col=0)
    df_result_aux.num_colecao = df_result_aux.num_colecao.map(formata_num_colecao_teste)
    df_result_aux = df_result_aux.fillna({'extras':'', 'lingua':''})
    chave = (df_result_aux.nome + df_result_aux.num_colecao.map(lambda x: str(x)))
    df_result_aux = df_result_aux[chave != chave.iloc[-1]] #remove último card procurado

if config.DEBUG:
    df = pd.DataFrame(data=[['Charizard', ('4/102'), 'foil', 'EN', 'NM']], columns=['nome', 'num_colecao', 'extras', 'lingua', 'condicao']) #testes
    #df = pd.DataFrame(data=[['Mew', ('19/165'), 'foil', 'EN', 'NM']], columns=['nome', 'num_colecao', 'extras', 'lingua', 'condicao']) #testes
    df.num_colecao = df.num_colecao.map(formata_num_colecao) #testes
    driver = carrega_driver(website=config.WEBSITE_1, headless=False) #testes
else:
    driver = carrega_driver(website=config.WEBSITE_1, headless=True)

#-------------------------------Busca primeiro na Liga Pokemon----------------------------
result_pokemon_website_1 = list()
preco_acumulado = 0
cards_ja_buscados = set() #rastreia os cards das coleções já buscadas para não duplicar
if df_result_aux is not None:
    cards_ja_buscados = set(df_result_aux[['nome', 'num_colecao']].apply(lambda x: (x.nome, x.num_colecao), axis=1)) #inicializa caso va reutilizar um resultado anterior
df = df[~df.condicao.isna()].groupby(df.columns.to_list(), dropna=False, as_index=False, sort=False).size()
df = df.fillna('')
if config.BUSCA_WEBSITE_1:
    for idx, row in df.iterrows(): #busca cada 'nome' em df
        if (row['nome'], row['num_colecao']) not in cards_ja_buscados:
            cards_ja_buscados.add((row['nome'], row['num_colecao']))

            n_tentativas_colecao = 0
            colecao = None
            while (colecao == None) and (n_tentativas_colecao <= config.N_MAX_TENTATIVAS_COLECAO):
                #--------------Inicia primeira busca pelo nome----------------------------
                print('Procurando todos os {} coleção {}'.format(row['nome'], row['num_colecao']))
                busca_nome(driver=driver, nome=row['nome'], timeout=config.TIMEOUT_BUSCA_PRINCIPAL)
                # ------------------------------------------------------------------------
                # -------------Loop para carregar todos na página ("Exibir mais")---------
                clica_exibir_mais(driver=driver, timeout=config.TIMEOUT_EXIBIR_MAIS)
                # ------------------------------------------------------------------------
                #--------------Procura dentre as coleções que apareceram no site----------
                colecao, codigo_colecao = procura_colecao(driver, row['num_colecao'], config)
                # ------------------------------------------------------------------------
                n_tentativas_colecao = n_tentativas_colecao + 1
                if colecao: #caso tenha encontrado alguma igual ao df
                    seleciona_colecao(colecao=colecao, driver=driver, timeout=config.TIMEOUT_SELECIONA_CARD)
                    clica_exibir_mais(driver=driver, timeout=config.TIMEOUT_EXIBIR_MAIS)

                    linhas = driver.find_elements_by_class_name('estoque-linha.ecom-marketplace')
                    for linha in linhas:
                        qualidade_card = linha.find_element_by_class_name('e-col4').text
                        lingua_card = retorna_lingua_card(linha=linha)
                        try:
                            extras = linha.find_element_by_class_name('e-mob-extranw').get_attribute('innerHTML')
                        except NoSuchElementException:
                            extras = ''

                        aperta_comprar(linha=linha, espera_botao_comprar=config.ESPERA_BOTAO_COMPRAR)
                        preco_unitario = retorna_preco_liga(driver, preco_acumulado, timeout=config.TIMEOUT_BOTAO_CARRINHO)
                        n_tentativas_preco = 0
                        while (preco_unitario == 0) and (n_tentativas_preco <= config.N_MAX_TENTATIVAS_PRECO):
                            print('preco_unitario = {}, tentando coletar preço novamente'.format(preco_unitario))
                            preco_unitario = retorna_preco_liga(driver, preco_acumulado, timeout=config.TIMEOUT_BOTAO_CARRINHO)
                            n_tentativas_preco = n_tentativas_preco + 1
                        if preco_unitario == 0:
                            preco_unitario = np.nan
                        else:
                            preco_acumulado = preco_acumulado + preco_unitario

                        card_info = (row['nome'], codigo_colecao, extras, lingua_card, qualidade_card, preco_unitario)
                        print((card_info[:-1]) + (round(card_info[-1], 2),)) #print na tela arredondando o último valor ("preco_unitario")
                        result_pokemon_website_1.append(card_info)
                    df_result_complemento = pd.DataFrame(result_pokemon_website_1,
                                             columns=df.columns.drop('size').append(pd.Index(['preco_unitario'])))
                    if df_result_aux is not None:
                        df_result = df_result_aux.append(df_result_complemento, ignore_index=True)
                    else:
                        df_result = df_result_complemento.copy()
                    #trata lingua multipla, com condicao por exemplo "Português / Inglês"
                    aux_lingua = df_result[df_result.lingua.map(lambda x: '/' in x)].lingua.map(lambda x: x.split('/'))
                    idx_copias = aux_lingua.index
                    df_result.loc[idx_copias, ('lingua')] = aux_lingua.map(lambda x: x[0].strip()) #altera para a primeira lingua
                    aux_df = df_result.loc[idx_copias].copy()
                    aux_df.loc[idx_copias, ('lingua')] = aux_lingua.map(lambda x: x[1].strip()) #altera para a segunda lingua
                    df_result = df_result.append(aux_df, ignore_index=True) #adiciona as linhas da segunda lingua
                    df_result = df_result.sort_values(['num_colecao', 'preco_unitario']).reset_index(drop=True)

                    salva_dados(df=df_result.assign(preco_unitario=df_result.preco_unitario.round(2)), nome_arquivo=config.CSV_OUTPUT_TODOS)
                    dtypes_dict = {
                        'extras': str,
                        'lingua': str,
                        'condicao': str
                    }
                    #TODO - fazer com que a média use linguas como Portugues / Ingles para portugues por exemplo
                    #df_result_media = df_result.groupby(df_result.columns.drop('preco_unitario').to_list(), as_index=False, sort=False).mean()
                    df_result_media = df_result.groupby(df_result.columns.drop('preco_unitario').to_list(), as_index=False, sort=False).min()
                    df_result_media = df_result_media.applymap(lambda x: x.lower() if type(x) == str else x).astype(dtypes_dict)
                    df_result_media.preco_unitario = df_result_media.preco_unitario.round(2)
                    df_merge = df.applymap(lambda x: x.lower() if type(x) == str else x).astype(dtypes_dict).merge(df_result_media,
                                                                                                        how='left',
                                                                                                        on=['nome',
                                                                                                            'num_colecao',
                                                                                                            'extras',
                                                                                                            'lingua',
                                                                                                            'condicao'])
                    df_merge['preco_total'] = df_merge['preco_unitario'] * df_merge['size']
                    df_merge.preco_total = df_merge.preco_total.round(2)
                    salva_dados(df=df_merge, nome_arquivo=config.CSV_OUTPUT_MERGE)
                else:
                    print('Não foi encontrada esta coleção')
#-----------------------------------------------------------------------------------------

#-------------------------------Depois busca no Ebay--------------------------------------
if config.BUSCA_WEBSITE_2:
    driver.get(config.WEBSITE_2)
    result_pokemon_website_2 = list()
    cards_ja_buscados = set() #rastreia os cards das coleções já buscadas para não duplicar
    for idx, row in df.iterrows(): #busca cada 'nome' em df
        if (row['nome'], row['num_colecao'], row['extras'], row['lingua'], row['condicao']) not in cards_ja_buscados:
            cards_ja_buscados.add((row['nome'], row['num_colecao'], row['extras'], row['lingua'], row['condicao']))

            #--------------Inicia busca pelo card na "Pesquisa Avançada"----------------------------
            print('Procurando todos os {} coleção {}'.format(row['nome'], row['num_colecao']))
            carrega_busca_avancada(driver=driver, config=config, row=row)
            # ------------------------------------------------------------------------

            produtos = driver.find_elements_by_class_name('sresult.lvresult.clearfix.li')
            for produto in produtos:
                preco = retorna_preco_ebay(produto=produto)
                is_psa = verifica_psa(produto=produto)
                is_nome = verifica_nome(row=row, produto=produto)

                if not ((not is_psa) and is_nome): #verifica se existe a string 'psa' no nome (e não insere o preço) e se existe o nome ou alguma parte do nome na string do produto
                    preco = np.nan
                card_info = (row['nome'], row['num_colecao'], row['extras'], row['lingua'], row['condicao'], round(preco, 2))
                print(card_info)
                result_pokemon_website_2.append(card_info)
                df_result = pd.DataFrame(result_pokemon_website_2, columns=df.columns.append(pd.Index(['preco'])))
                salva_dados(df=df_result, nome_arquivo=config.CSV_OUTPUT_EBAY)
                dtypes_dict = {
                    'extras': str,
                    'lingua': str,
                    'condicao': str
                }
                #salva_dados(df=df.applymap(lambda x: x.lower() if type(x) == str else x).astype(dtypes_dict).merge(df_result.applymap(lambda x: x.lower() if type(x) == str else x).astype(dtypes_dict), how='left', on=['nome', 'num_colecao', 'extras', 'lingua', 'condicao']), nome_arquivo=config.CSV_OUTPUT_MERGE)
#-----------------------------------------------------------------------------------------
