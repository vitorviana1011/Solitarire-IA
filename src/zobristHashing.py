import random
from card import Suit, Symbol
from gameState import GameState

SUITS = list(Suit)
SYMBOLS = list(Symbol)  

def card_index(suit: Suit, symbol: Symbol) -> int:
    return SUITS.index(suit) * 13 + SYMBOLS.index(symbol)

# Posições do tabuleiro:
#   0..6   colunas 0-6 do tableau (profundidade por posição: até 20 cartas)
#   7..10  fundações 0-3
#   11     stock
#   12     waste

NUM_CARDS = 52      # número de cartas no baralho
NUM_POSITIONS = 13  # número de posições possíveis
MAX_DEPTH = 52      # profundidade máxima por pilha

# Ao fixar a semente com 0xDEADBEEF_CAFECAFE, o Python sempre gerará os mesmos números
# aleatórios de 64 bits toda vez que o script for executado.
# Isso garante que a IA ou o Solver avalie o mesmo tabuleiro da mesma forma em 
# qualquer computador, permitindo testes idênticos.
RNG = random.Random(0xDEADBEEF_CAFECAFE)

ZOBRIST_TABLE: list[list[list[int]]] = [
    [
        [
            #gerar números de 64 bits é crucial para evitar colisões de hash
            RNG.getrandbits(64) for _ in range(MAX_DEPTH)
        ] 
        for _ in range(NUM_POSITIONS)
    ] 
    for _ in range(NUM_CARDS)
]

ZOBRIST_FLIPPED: list[list[list[int]]] = [
    [
        [
            RNG.getrandbits(64) for _ in range(MAX_DEPTH)
        ]
        for _ in range(NUM_POSITIONS)
    ]
    for _ in range(NUM_CARDS)
]

#converte índice de pilha (GameState) para índice de posição Zobrist
def pos_index(stack_index: int) -> int:
    return stack_index

# h ^= valor é atalho para h = h ^ valor (XOR exclusivo)
# ela é a própria inversa
# Se você aplicar o XOR com a carta pela primeira vez, você insere a carta na assinatura do tabuleiro.
# Se você aplicar o XOR com a mesma carta pela segunda vez, você remove a carta da assinatura.

def compute_hash(state: "GameState") -> int:
    h = 0
    for pos_idx, stack in enumerate(state.all_stacks()):
        for depth, (suit, symbol, flipped) in enumerate(stack):
            cardIndex = card_index(suit, symbol)
    
            h ^= ZOBRIST_TABLE[cardIndex][pos_idx][depth] 
            if flipped:
                h ^= ZOBRIST_FLIPPED[cardIndex][pos_idx][depth]
    return h

def update_hash(h: int, suit: Suit, symbol: Symbol, from_pos: int, from_depth: int, to_pos: int, to_depth: int,flipped: bool) -> int:
    cardIndex = card_index(suit, symbol)
    
    h ^= ZOBRIST_TABLE[cardIndex][from_pos][from_depth]
    if flipped:
        h ^= ZOBRIST_FLIPPED[cardIndex][from_pos][from_depth]
    
    h ^= ZOBRIST_TABLE[cardIndex][to_pos][to_depth]
    if flipped:
        h ^= ZOBRIST_FLIPPED[cardIndex][to_pos][to_depth]
        
    return h

def flip_hash(h: int, suit: Suit, symbol: Symbol, pos: int, depth: int) -> int:
    cardIndex = card_index(suit, symbol)

    h ^= ZOBRIST_FLIPPED[cardIndex][pos][depth]

    return h