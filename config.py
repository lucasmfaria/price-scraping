import numpy as np

BUSCA_WEBSITE_1 = True
BUSCA_WEBSITE_2 = False
WEBSITE_1 = 'https://www.ligapokemon.com.br/'
#CSV_INPUT = 'cartas_pokemon.csv'
CSV_INPUT = 'cartas_pokemon_base_set.csv'
#CSV_OUTPUT_TODOS = 'preco_todos_ligapokemon.csv'
CSV_OUTPUT_TODOS = 'preco_todos_ligapokemon_base_set.csv'
#CSV_OUTPUT_MERGE = 'preco_input_ligapokemon.csv'
CSV_OUTPUT_MERGE = 'preco_input_ligapokemon_base_set.csv'

WEBSITE_2 = 'https://www.ebay.com/'
CSV_OUTPUT_EBAY = 'preco_todos_ebay.csv'

LINGUAS_POSSIVEIS = ['Inglês', 'Português', 'Português / Inglês', 'Japonês', 'Espanhol']

TIMEOUT_BUSCA_PRINCIPAL = 10
TIMEOUT_EXIBIR_MAIS = 10
TIMEOUT_SELECIONA_CARD = 10
TIMEOUT_BOTAO_CARRINHO = 10
ESPERA_BOTAO_COMPRAR = 1.5
N_MAX_TENTATIVAS_PRECO = 10

DEBUG = False

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
