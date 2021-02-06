import PySimpleGUI as sg
from pathlib import Path
import pandas as pd
import config
import numpy as np
from utils.scraper import LigaPokemonScraper

def formata_num_colecao(num_colecao, com_parenteses=False):
    if com_parenteses == False:
        split = str(num_colecao).split('/')
    elif com_parenteses == True:
        split = str(num_colecao).split('(')[-1].split(')')[0].split(', ')
    if len(split) > 1: #trata casos com "/" no meio, exemplo "1/102"
        try: #trata casos aonde cada elemento é um número
            retorno = (int(split[0]), int(split[1]))
        except ValueError: #trata casos aonde cada elemento possui alfanumérico
            retorno = (split[0], split[1])
        return retorno
    else: #trata casos sem "/" no meio, exemplo "SH10"
        return num_colecao

def carrega_lista_cards(path):
    df = pd.read_csv(path, sep=';', dtype=config.DTYPES_DICT)
    df = df.applymap(lambda x: x.strip() if type(x) == str else x)
    df.num_colecao = df.num_colecao.map(formata_num_colecao)
    #df = df.where(pd.notnull(df), None) #substitui NaN por None
    df = df[~df.condicao.isna()].groupby(df.columns.to_list(), dropna=False, as_index=False, sort=False).size()
    df = df.fillna('')
    return df

def carrega_lista_precos(path):
    df = pd.read_csv(path, sep=';', dtype=config.DTYPES_DICT, index_col=0)
    df.num_colecao = df.num_colecao.map(lambda x: formata_num_colecao(x, com_parenteses=True))
    df = df.fillna({'extras': '', 'lingua': ''})
    chave = (df.nome + df.num_colecao.map(lambda x: str(x)))
    df = df[chave != chave.iloc[-1]]  # remove último card procurado (pois pode ter parado no meio da busca e não ter completado aquele card
    return df

def constroi_resultados(precos_list, df_precos_parcial, df_cards, config, path):
    df_precos_complemento = pd.DataFrame(precos_list,
                                         columns=df_cards.columns.drop('size').append(
                                             pd.Index(['preco_unitario'])))
    if df_precos_parcial is not None:
        df_precos = df_precos_parcial.append(df_precos_complemento, ignore_index=True)
    else:
        df_precos = df_precos_complemento.copy()
    # trata lingua multipla, com condicao por exemplo "Português / Inglês"
    aux_lingua = df_precos[df_precos.lingua.map(lambda x: '/' in x)].lingua.map(lambda x: x.split('/'))
    idx_copias = aux_lingua.index
    df_precos.loc[idx_copias, ('lingua')] = aux_lingua.map(
        lambda x: x[0].strip())  # altera para a primeira lingua
    aux_df = df_precos.loc[idx_copias].copy()
    aux_df.loc[idx_copias, ('lingua')] = aux_lingua.map(
        lambda x: x[1].strip())  # altera para a segunda lingua
    df_precos = df_precos.append(aux_df, ignore_index=True)  # adiciona as linhas da segunda lingua
    df_precos = df_precos.sort_values(['num_colecao', 'preco_unitario']).reset_index(drop=True)

    df_precos.assign(preco_unitario=df_precos.preco_unitario.round(2)).to_csv(path / config.CSV_OUTPUT_TODOS, sep=';')
    dtypes_dict = {
        'extras': str,
        'lingua': str,
        'condicao': str
    }
    if config.ESTATISTICA == 'media':
        df_precos_estatistica = df_precos.groupby(df_precos.columns.drop('preco_unitario').to_list(), as_index=False,
                                                  sort=False).mean()
    elif config.ESTATISTICA == 'minimo':
        df_precos_estatistica = df_precos.groupby(df_precos.columns.drop('preco_unitario').to_list(), as_index=False,
                                                  sort=False).min()
    df_precos_estatistica = df_precos_estatistica.applymap(lambda x: x.lower() if type(x) == str else x).astype(
        dtypes_dict)
    df_precos_estatistica.preco_unitario = df_precos_estatistica.preco_unitario.round(2)
    df_merge = df_cards.applymap(lambda x: x.lower() if type(x) == str else x).astype(dtypes_dict).merge(
        df_precos_estatistica,
        how='left',
        on=['nome',
            'num_colecao',
            'extras',
            'lingua',
            'condicao'])
    df_merge['preco_total'] = df_merge['preco_unitario'] * df_merge['size']
    df_merge.preco_total = df_merge.preco_total.round(2)
    df_merge.to_csv(path / config.CSV_OUTPUT_MERGE, sep=';')

# First the window layout in 2 columns
cards_input_column = [
    [
        sg.Text("Arquivo de cards"),
        sg.In(size=(25, 1), enable_events=True, key="-CARDS FILENAME-"),
        sg.FileBrowse(file_types=(("csv Files", "*.csv"),))
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 20), key="-CARDS LIST-"
        )
    ]
]

botao_column = [
    [
        sg.Button("BUSCA", key='-BUSCA-')
    ]
]

precos_input_column = [
    [
        sg.Text("Arquivo de precos parcial (caso necessário)"),
        sg.In(size=(25, 1), enable_events=True, key="-PRECOS FILENAME-"),
        sg.FileBrowse(file_types=(("csv Files", "*.csv"),))
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 20), key="-PRECOS LIST-"
        )
    ],
]

# ----- Full layout -----
layout = [
    [
        sg.Column(cards_input_column),
        sg.Column(botao_column),
        sg.Column(precos_input_column),
    ]
]

window = sg.Window("Card Scraper", layout)
df_precos_parcial = None

# Run the Event Loop
while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    if event == "-CARDS FILENAME-":
        csv_input_path = values["-CARDS FILENAME-"]
        try:
            df_cards = carrega_lista_cards(Path(csv_input_path))
        except:
            print("Não foi possível ler o arquivo .csv")

        window["-CARDS LIST-"].update(df_cards.to_numpy().tolist())

    if event == "-PRECOS FILENAME-":
        precos_input_path = values["-PRECOS FILENAME-"]
        try:
            df_precos_parcial = carrega_lista_precos(Path(precos_input_path))
        except:
            print("Não foi possível ler o arquivo .csv")
        else:
            window["-PRECOS LIST-"].update(df_precos_parcial.to_numpy().tolist())

    elif event == "-BUSCA-":
        try:
            precos_website_1 = list()
            preco_acumulado = 0
            cards_ja_buscados = set()  # rastreia os cards das coleções já buscadas para não duplicar
            if df_precos_parcial is not None:
                cards_ja_buscados = set(
                    df_precos_parcial[['nome', 'num_colecao']].apply(lambda x: (x.nome, x.num_colecao),
                                                                     axis=1))  # inicializa caso va reutilizar um resultado anterior

            scraper = LigaPokemonScraper(correcoes_num_colecao=config.CORRECOES_NUMERO_COLECAO,
                                         website=config.WEBSITE_1,
                                         timeout_busca_principal=config.TIMEOUT_BUSCA_PRINCIPAL,
                                         timeout_exibir_mais=config.TIMEOUT_EXIBIR_MAIS,
                                         timeout_seleciona_card=config.TIMEOUT_SELECIONA_CARD,
                                         timeout_botao_carrinho=config.TIMEOUT_BOTAO_CARRINHO,
                                         espera_botao_comprar=config.ESPERA_BOTAO_COMPRAR,
                                         n_max_tentativas_preco=config.N_MAX_TENTATIVAS_PRECO,
                                         n_max_tentativas_colecao=config.N_MAX_TENTATIVAS_COLECAO,
                                         debug=config.DEBUG)
            for idx, row in df_cards.iterrows():  # busca cada 'nome' em df_cards
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

                            card_info = (
                            row['nome'], codigo_colecao, extras, lingua_card, qualidade_card, preco_unitario)
                            print((card_info[:-1]) + (
                                round(card_info[-1],
                                      2),))  # print na tela arredondando o último valor ("preco_unitario")
                            precos_website_1.append(card_info)
                        constroi_resultados(precos_website_1, df_precos_parcial, df_cards, config, Path(csv_input_path).parent)
                    else:
                        print('Não foi encontrada esta coleção')
        except Exception as e:
            print(e)

window.close()