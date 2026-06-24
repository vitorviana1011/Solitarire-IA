# Solitaire AI
Algoritmo A* implementado em python para resolução do jogo de cartas Paciência (Klond like)

Unica implementação feita foi os algoritmos de busca, as regras do jogo e interface foram desenvolvidas por: João Pereira (Github: ttoino) e Ricardo Cruz (Github: rpmcruz)
Link do repositorio: https://github.com/ttoino/feup-fpro-solitaire

## Funcionalidades Implementadas
* Algoritmo A* (BuscaAEstrela) rodando em background (multi-threading) para encontrar o caminho ideal até a vitória.
* Sistema Zobrist para melhor organização do tabuleiro.
* Tela de vitória que exibe a transcrição dos movimentos realizados (Histórico ou Caminho da IA).

## Pré-requisitos

Para executar este projeto, você precisará do Python 3 instalado em sua máquina, além das seguintes bibliotecas:

* `pygame`: Para a renderização gráfica e loop principal do jogo.
* `cairosvg`: Para converter os assets em SVG das cartas para superfícies do Pygame.

## Como executar:
Clone o repositório ou baixe os arquivos fonte. Certifique-se de que a pasta assets (e suas subpastas contendo os ícones e SVGs das cartas) esteja no mesmo diretório dos scripts Python.

Para iniciar o jogo, execute o arquivo principal:
* `python main.py`

## Teclas Implementadas
* A: Executar a Inteligência Artificial (Algoritmo A*). O jogo será resolvido sozinho se houver solução.

## Estrutura do Projeto
* main.py: Loop principal do Pygame, gerenciamento de eventos, atalhos de teclado e inicialização de threads para a IA.

* game.py: Lógica central do jogo, regras, movimentação, interações de mouse e controle das pilhas de cartas (Tableau, Foundation, Stock, Waste).

* ui.py: Gerenciamento da Interface de Usuário (Menus, botões e telas Home/Game/Win).

* move.py: Implementação do padrão de projeto Command, registrando cada ação para o sistema de Undo/Redo e tradução textual dos movimentos.

* animation.py: Classes abstratas e concretas responsáveis por animar a transição gráfica das cartas.

* assets.py: Carregador de recursos visuais que converte imagens SVG para superfícies Pygame.

* card.py e stack.py: Definição das classes das cartas, naipes, símbolos e dos contêineres de cartas do tabuleiro.

* history.py: Pilha que mantém o registro das instâncias de movimentos realizados.

* gameState.py: Modelagem do estado atual do jogo sem dependências gráficas, otimizada para avaliação rápida da IA.

* buscaAEstrela.py Implementação dos algoritmos de busca e heurísticas.

* constants.py: Definição de constantes de cores, medidas, posições e taxa de atualização gráfica.

### Busca Profundidade
Existe a classe e arquivo busca por profundidade que foi abandonada no meio do projeto, se quiser tentar consertar.