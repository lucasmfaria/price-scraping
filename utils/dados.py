import pandas as pd
from pathlib import Path

def carrega_lista_cards(config):
    if config.DEBUG == False:
        df = pd.read_csv(Path('./data') / config.CSV_INPUT, sep=';', dtype=config.DTYPES_DICT)
    elif config.DEBUG == True: #testes
        df = pd.DataFrame(data=[['Charizard', ('4/102'), 'foil', 'EN', 'NM']],
                          columns=['nome', 'num_colecao', 'extras', 'lingua', 'condicao'])
        #df = pd.DataFrame(data=[['Mew', ('19/165'), 'foil', 'EN', 'NM']], columns=['nome', 'num_colecao', 'extras', 'lingua', 'condicao'])
    df = df.applymap(lambda x: x.strip() if type(x) == str else x)
    df.num_colecao = df.num_colecao.map(formata_num_colecao)
    #df = df.where(pd.notnull(df), None) #substitui NaN por None
    df = df[~df.condicao.isna()].groupby(df.columns.to_list(), dropna=False, as_index=False, sort=False).size()
    df = df.fillna('')
    return df

def carrega_lista_precos(config):
    if config.CONTINUAR_DE_ONDE_PAROU:
        df = pd.read_csv(Path('./data') / config.CSV_OUTPUT_TODOS, sep=';', dtype=config.DTYPES_DICT, index_col=0)
        df.num_colecao = df.num_colecao.map(lambda x: formata_num_colecao(x, com_parenteses=True))
        df = df.fillna({'extras': '', 'lingua': ''})
        chave = (df.nome + df.num_colecao.map(lambda x: str(x)))
        df = df[chave != chave.iloc[-1]]  # remove último card procurado (pois pode ter parado no meio da busca e não ter completado aquele card
    else:
        df = None
    return df

def salva_dados(df, nome_arquivo):
    df.to_csv(Path('./data') / nome_arquivo, sep=';')
    return df

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

def checa_colecao(codigo_colecao, codigo_colecao_df):
    codigo_colecao_aux = codigo_colecao.split('(')[-1].split(')')[0]
    codigo_colecao_aux = formata_num_colecao(codigo_colecao_aux) #formata para transformar em numeros (caso compare em string pode ocorrer zero a esquerda)
    if codigo_colecao_aux == codigo_colecao_df:  # caso tenha encontrado o pokemon da linha em questão
        return True
    else:
        return False

def extrai_preco_string(string):
    return float(string.split(' ')[-1].replace('.', '').replace(',', '.'))