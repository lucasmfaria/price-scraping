# Busca de preços - Cards Pokémon
Este projeto visa facilitar a busca de preços nos sites referência de cards de Pokémon TCG (Trading Card Game) utilizando Python, Selenium e Pandas.
Atualmente o usuário precisa buscar o preço de cada item manualmente de cada vez e preencher seu controle interno de preços de seus cards. Tendo em vista esta dificuldade, desenvolvi este utilitário.

Forma de usar: preencher o arquivo "cartas_pokemon.csv" com os cards. Cada "nome/num_colecao" será uma busca. Construir um ambiente virtual python e instalar libs em "requirements.txt". Rodar "app.py".

Testado apenas com Python 3.7.9. Versões das bibliotecas no "requirements.txt". Foi utilizado o chromedriver para rodar o Selenium. Para instalação deste driver, verificar https://selenium-python.readthedocs.io/installation.html#drivers.

Funcionalidades:
- Busca na Liga Pokémon (https://www.ligapokemon.com.br/)
- Interface gráfica
- Opção de continuar de onde parou em uma rodada anterior
- Correção do número da coleção conforme utilizado no site da Liga Pokémon (via config.py), caso contrário não encontraria coleções com números alterados

TODO:
- Contabilizar não apenas os preços, mas as unidades disponiveis também, e com isso considerar a média dos menores preços que cobrem a quantidade desejada
- Busca no Ebay

Obs:
- Qualquer mudança no layout do site da Liga Pokémon pode ocasionar erro neste utilitário.
- Não me responsabilizarei por possíveis preços errados retornados pelo utilitário. O intuito é ajudar a extrair apenas, portanto antes de fazer qualquer negócio é necessária a supervisão dos preços por parte do usuário.