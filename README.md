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

## Executando a IA
* Após iniciar o jogo, espere a animação das cartas. Assim que todas as carats estiveram na posição inicial, pressione a tecla ¨A¨. O jogo será resolvido sozinho se houver solução.

## Sistema de Sementes (Seed) e Reprodutibilidade

O projeto conta com um sistema de sementes para o gerador de números pseudo-aleatórios do Python. Esta funcionalidade é para garantir que o problema tenha solução no teste da IA.

No ponto de entrada do programa, a semente é definida explicitamente:
* **Configuração:** O valor padrão definido no código é a semente `46`.
* **Demonstração:** O código possui indicações para testes com as sementes `43`, `44` e `46`, que servem para demonstrar o funcionamento correto e a capacidade de resolução dos algoritmos de busca. A seed `45` não possui solução e o algoritmo roda indefinidamente procurando uma solução.

Ao alterar o valor numérico passado para a função de semente, o processo de embaralhamento inicial gera um layout de jogo completamente diferente para as colunas do tabuleiro.

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