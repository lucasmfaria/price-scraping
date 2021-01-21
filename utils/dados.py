import pandas as pd
from pathlib import Path

def carrega_dados(config):
    df = pd.read_csv(Path('./data') / config.CSV_NAME, sep=';')
    df.num_colecao = df.num_colecao.map(formata_num_colecao)
    return df

def formata_num_colecao(num_colecao):
    split = str(num_colecao).split('/')
    try:
        retorno = (int(split[0]), int(split[1]))
    except ValueError:
        retorno = (split[0], split[1])
    return retorno