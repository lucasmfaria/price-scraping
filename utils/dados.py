
def formata_num_colecao(num_colecao):
    split = str(num_colecao).split('/')
    try:
        retorno = (int(split[0]), int(split[1]))
    except ValueError:
        retorno = (split[0], split[1])
    return retorno