import PySimpleGUI as sg
from pathlib import Path
import config
import numpy as np
from utils.scraper import LigaPokemonScraper
from utils.dados import carrega_lista_precos, carrega_lista_cards, constroi_resultados, carrega_cards_ja_buscados

class App:
    def __init__(self):
        self.reset()

    def reset(self):
        # Input da lista de cards que o usuário quer buscar os preços
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
                sg.Combo(['Preços Mínimos', 'Preços Médios'], key='-COMBO-')
            ],
            [
                sg.Button("BUSCA", key='-BUSCA-')
            ]
        ]

        # Input da lista de preços parcial (caso queira rodar a partir deste ponto)
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

        layout = [
            [
                sg.Column(cards_input_column),
                sg.Column(botao_column),
                sg.Column(precos_input_column)
            ],
            [
                sg.ProgressBar(1, orientation='h', size=(100, 20), key='-PROGRESS-')
            ]
        ]

        self.window = sg.Window("Card Scraper", layout)
        self.df_precos_parcial = None
        self.df_cards = None
        self.cards_ja_buscados = set()
        self.progress_bar = self.window.FindElement('-PROGRESS-')

    def run(self):
        # Loop de eventos
        while True:
            event, values = self.window.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                break

            if event == "-CARDS FILENAME-":
                csv_input_path = values["-CARDS FILENAME-"]
                try:
                    self.df_cards = carrega_lista_cards(Path(csv_input_path), config)
                except:
                    print("Não foi possível ler o arquivo .csv")
                else:
                    self.window["-CARDS LIST-"].update(self.df_cards.to_numpy().tolist())

            if event == "-PRECOS FILENAME-":
                precos_input_path = values["-PRECOS FILENAME-"]
                try:
                    self.df_precos_parcial = carrega_lista_precos(Path(precos_input_path), config)
                    self.cards_ja_buscados = carrega_cards_ja_buscados(self.df_precos_parcial)
                except:
                    print("Não foi possível ler o arquivo .csv")
                else:
                    self.window["-PRECOS LIST-"].update(self.df_precos_parcial.to_numpy().tolist())

            elif (event == "-BUSCA-") and (values['-COMBO-'] != ''):
                try:
                    if values['-COMBO-'] == 'Preços Mínimos':
                        estatistica = 'minimo'
                    elif values['-COMBO-'] == 'Preços Médios':
                        estatistica = 'media'
                    precos_website_1 = list()
                    preco_acumulado = 0

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
                    for idx, row in self.df_cards.iterrows():  # busca cada 'nome' em df_cards
                        self.progress_bar.UpdateBar(len(self.cards_ja_buscados), self.df_cards.shape[0])
                        if (row['nome'], row['num_colecao']) not in self.cards_ja_buscados:
                            self.cards_ja_buscados.add((row['nome'], row['num_colecao']))

                            print('Procurando todos os {} coleção {}'.format(row['nome'], row['num_colecao']))
                            precos_website_1, preco_acumulado = scraper.busca(row['nome'], row['num_colecao'],
                                                                precos_website_1, preco_acumulado, self.df_precos_parcial,
                                                                              self.df_cards, estatistica, csv_input_path)
                    self.window.close()
                    self.reset()
                except Exception as e:
                    print(e)
        self.window.close()

if __name__ == "__main__":
    app = App()
    app.run()