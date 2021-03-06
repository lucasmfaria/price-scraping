import numpy as np

BUSCA_WEBSITE_1 = True
BUSCA_WEBSITE_2 = False
WEBSITE_1 = 'https://www.ligapokemon.com.br/'
TIMEOUT_BUSCA_PRINCIPAL = 10
TIMEOUT_EXIBIR_MAIS = 8
TIMEOUT_SELECIONA_CARD = 8
TIMEOUT_BOTAO_CARRINHO = 4
ESPERA_BOTAO_COMPRAR = 1
N_MAX_TENTATIVAS_PRECO = 16
N_MAX_TENTATIVAS_COLECAO = 3
DEBUG = False

DTYPES_DICT = {
        'nome': str,
        'num_colecao': str,
        'extras': str,
        'lingua': str,
        'condicao': str,
        'preco_unitario': float,
    }

''' Lista de correções do número de cada coleção
Team Aqua vs Team Magma /95 -> /97
Aquapolis -> H32 -> /147
Ex Dragon /97 -> /100
Arceus /99 -> /111
Delta Species /113 -> /114
Platinum /127 -> /133
Hidden Legends /101 -> /102
Rising Rivals /111 -> /120
Supreme Victors /147 -> 153
Rocket returns /109 -> /111
Misterious Treasures /123 -> 124
'''
CORRECOES_NUMERO_COLECAO = {
    95:97,
    'H32':147,
    97:100,
    99:111,
    113:114,
    127:133,
    101:102,
    111:120,
    147:153,
    109:111,
    123:124,
}

WEBSITE_2 = 'https://www.ebay.com/'
CSV_OUTPUT_EBAY = 'preco_todos_ebay.csv'

DICT_LINGUA = {
        'português': 'portuguese',
        'inglês': 'english'
    }
DICT_CONDICAO = {
    'nm': 'near mint',
    'hp': 'hardly played',
    'mp': 'moderately played',
    'sp': 'slightly played',
    'd': 'damaged'
}
DICT_EXTRAS = {
    'foil': '',
    'reverse foil': 'reverse holo',
    'Foil': '',
    'Reverse Foil': 'reverse holo',
    np.nan: ''
}
