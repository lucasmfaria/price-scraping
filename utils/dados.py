import pandas as pd

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

def carrega_lista_cards(path, config):
    df = pd.read_csv(path, sep=';', dtype=config.DTYPES_DICT)
    df = df.applymap(lambda x: x.strip() if type(x) == str else x)
    df.num_colecao = df.num_colecao.map(formata_num_colecao)
    #df = df.where(pd.notnull(df), None) #substitui NaN por None
    df = df[~df.condicao.isna()].groupby(df.columns.to_list(), dropna=False, as_index=False, sort=False).size()
    df = df.fillna('')
    return df

def carrega_lista_precos(path, config):
    df = pd.read_csv(path, sep=';', dtype=config.DTYPES_DICT, index_col=0)
    df.num_colecao = df.num_colecao.map(lambda x: formata_num_colecao(x, com_parenteses=True))
    df = df.fillna({'extras': '', 'lingua': ''})
    chave = (df.nome + df.num_colecao.map(lambda x: str(x)))
    df = df[chave != chave.iloc[-1]]  # remove último card procurado (pois pode ter parado no meio da busca e não ter completado aquele card
    return df

def checa_colecao(codigo_colecao, codigo_colecao_df):
    codigo_colecao_aux = codigo_colecao.split('(')[-1].split(')')[0]
    codigo_colecao_aux = formata_num_colecao(codigo_colecao_aux) #formata para transformar em numeros (caso compare em string pode ocorrer zero a esquerda)
    if codigo_colecao_aux == codigo_colecao_df:  # caso tenha encontrado o pokemon da linha em questão
        return True
    else:
        return False

def carrega_cards_ja_buscados(df_precos_parcial):
    cards_ja_buscados = set()  # rastreia os cards das coleções já buscadas para não duplicar
    if df_precos_parcial is not None:
        cards_ja_buscados = set(
            df_precos_parcial[['nome', 'num_colecao']].apply(lambda x: (x.nome, x.num_colecao),
                                                                  axis=1))  # inicializa caso va reutilizar um resultado anterior
    return cards_ja_buscados

def extrai_preco_string(string):
    return float(string.split(' ')[-1].replace('.', '').replace(',', '.'))

def constroi_resultados(precos_list, df_precos_parcial, df_cards, estatistica, path):
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

    df_precos.assign(preco_unitario=df_precos.preco_unitario.round(2)).to_csv(path.parent / (path.stem + '_preco_todos.csv'), sep=';')
    dtypes_dict = {
        'extras': str,
        'lingua': str,
        'condicao': str
    }
    if estatistica == 'media':
        df_precos_estatistica = df_precos.groupby(df_precos.columns.drop('preco_unitario').to_list(), as_index=False,
                                                  sort=False).mean()
    elif estatistica == 'minimo':
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
    df_merge.to_csv(path.parent / (path.stem + '_preco_input.csv'), sep=';')