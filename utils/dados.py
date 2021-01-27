import pandas as pd
from pathlib import Path

def carrega_dados(config):
    dtypes_dict = {
        'extras': str,
        'lingua': str,
        'condicao': str
    }
    df = pd.read_csv(Path('./data') / config.CSV_INPUT, sep=';', dtype=dtypes_dict)
    df.num_colecao = df.num_colecao.map(formata_num_colecao)
    df = df.where(pd.notnull(df), None) #substitui NaN por None
    return df

def salva_dados(df, nome_arquivo):
    df.to_csv(Path('./data') / nome_arquivo, sep=';')
    return df

def formata_num_colecao(num_colecao):
    split = str(num_colecao).split('/')
    try:
        retorno = (int(split[0]), int(split[1]))
    except ValueError:
        retorno = (split[0], split[1])
    return retorno

def checa_colecao(codigo_colecao, codigo_colecao_df):
    codigo_colecao_aux = codigo_colecao.split('(')[-1].split(')')[0]
    codigo_colecao_aux = formata_num_colecao(codigo_colecao_aux) #formata para transformar em numeros (caso compare em string pode ocorrer zero a esquerda)
    if codigo_colecao_aux == codigo_colecao_df:  # caso tenha encontrado o pokemon da linha em questão
        return True
    else:
        return False

def extrai_preco_string(string):
    return float(string.split(' ')[-1].replace('.', '').replace(',', '.'))