import pandas as pd
import numpy as np
from selenium.common.exceptions import NoSuchElementException
import config
from utils.dados import carrega_lista_cards, carrega_lista_precos, salva_dados
from utils.scraper import carrega_busca_avancada, retorna_preco_ebay, verifica_psa, verifica_nome, LigaPokemonScraper

df_cards = carrega_lista_cards(config=config)
df_result_aux = carrega_lista_precos(config=config)

#-------------------------------Busca primeiro na Liga Pokemon----------------------------
result_pokemon_website_1 = list()
preco_acumulado = 0
cards_ja_buscados = set() #rastreia os cards das coleções já buscadas para não duplicar
if df_result_aux is not None:
    cards_ja_buscados = set(df_result_aux[['nome', 'num_colecao']].apply(lambda x: (x.nome, x.num_colecao), axis=1)) #inicializa caso va reutilizar um resultado anterior

if config.BUSCA_WEBSITE_1:
    scraper = LigaPokemonScraper(correcoes_num_colecao=config.CORRECOES_NUMERO_COLECAO, website=config.WEBSITE_1,
                          timeout_busca_principal=config.TIMEOUT_BUSCA_PRINCIPAL,
                          timeout_exibir_mais=config.TIMEOUT_EXIBIR_MAIS,
                          timeout_seleciona_card=config.TIMEOUT_SELECIONA_CARD,
                          timeout_botao_carrinho=config.TIMEOUT_BOTAO_CARRINHO,
                          espera_botao_comprar=config.ESPERA_BOTAO_COMPRAR,
                          n_max_tentativas_preco=config.N_MAX_TENTATIVAS_PRECO,
                          n_max_tentativas_colecao=config.N_MAX_TENTATIVAS_COLECAO,
                          debug=config.DEBUG)
    for idx, row in df_cards.iterrows(): #busca cada 'nome' em df_cards
        if (row['nome'], row['num_colecao']) not in cards_ja_buscados:
            cards_ja_buscados.add((row['nome'], row['num_colecao']))

            print('Procurando todos os {} coleção {}'.format(row['nome'], row['num_colecao']))
            colecao, codigo_colecao = scraper.busca_card(row['nome'], row['num_colecao'])
            if colecao:
                scraper.seleciona_colecao(colecao)
                scraper.clica_exibir_mais()
                linhas = scraper.encontra_linhas()
                for linha in linhas:
                    qualidade_card = scraper.encontra_qualidade(linha)
                    lingua_card = scraper.encontra_lingua(linha)
                    extras = scraper.encontra_extras(linha)
                    scraper.aperta_comprar(linha)
                    preco_unitario = scraper.encontra_preco(preco_acumulado)

                    if preco_unitario == 0:
                        preco_unitario = np.nan
                    else:
                        preco_acumulado = preco_acumulado + preco_unitario

                    card_info = (row['nome'], codigo_colecao, extras, lingua_card, qualidade_card, preco_unitario)
                    print((card_info[:-1]) + (
                    round(card_info[-1], 2),))  # print na tela arredondando o último valor ("preco_unitario")
                    result_pokemon_website_1.append(card_info)

                df_result_complemento = pd.DataFrame(result_pokemon_website_1,
                                                     columns=df_cards.columns.drop('size').append(
                                                         pd.Index(['preco_unitario'])))
                if df_result_aux is not None:
                    df_result = df_result_aux.append(df_result_complemento, ignore_index=True)
                else:
                    df_result = df_result_complemento.copy()
                # trata lingua multipla, com condicao por exemplo "Português / Inglês"
                aux_lingua = df_result[df_result.lingua.map(lambda x: '/' in x)].lingua.map(lambda x: x.split('/'))
                idx_copias = aux_lingua.index
                df_result.loc[idx_copias, ('lingua')] = aux_lingua.map(
                    lambda x: x[0].strip())  # altera para a primeira lingua
                aux_df = df_result.loc[idx_copias].copy()
                aux_df.loc[idx_copias, ('lingua')] = aux_lingua.map(
                    lambda x: x[1].strip())  # altera para a segunda lingua
                df_result = df_result.append(aux_df, ignore_index=True)  # adiciona as linhas da segunda lingua
                df_result = df_result.sort_values(['num_colecao', 'preco_unitario']).reset_index(drop=True)

                salva_dados(df=df_result.assign(preco_unitario=df_result.preco_unitario.round(2)),
                            nome_arquivo=config.CSV_OUTPUT_TODOS)
                dtypes_dict = {
                    'extras': str,
                    'lingua': str,
                    'condicao': str
                }
                if config.ESTATISTICA == 'media':
                    df_result_estatistica = df_result.groupby(df_result.columns.drop('preco_unitario').to_list(), as_index=False, sort=False).mean()
                elif config.ESTATISTICA == 'minimo':
                    df_result_estatistica = df_result.groupby(df_result.columns.drop('preco_unitario').to_list(), as_index=False,
                                                    sort=False).min()
                df_result_estatistica = df_result_estatistica.applymap(lambda x: x.lower() if type(x) == str else x).astype(
                    dtypes_dict)
                df_result_estatistica.preco_unitario = df_result_estatistica.preco_unitario.round(2)
                df_merge = df_cards.applymap(lambda x: x.lower() if type(x) == str else x).astype(dtypes_dict).merge(
                    df_result_estatistica,
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

''' TODO -  busca no Ebay
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

'''