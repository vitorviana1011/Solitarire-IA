from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Iterator
from card import Suit, Symbol

CardTuple = Tuple[Suit, Symbol, bool]  # (naipe, simbolo, virada)
StackTuples = List[CardTuple]

# Índices constantes
IDX_TABLEAU_START   = 0
IDX_TABLEAU_END     = 7
IDX_FOUNDATION_START= 7
IDX_FOUNDATION_END  = 11
IDX_STOCK           = 11
IDX_WASTE           = 12
NUM_STACKS          = 13

@dataclass
class GameState:
    stacks: List[StackTuples] = field(default_factory=lambda: [[] for _ in range(NUM_STACKS)])
    g: int = 0  # Custo acumulado
    f: int = 0  # f(n) = g(n) + h(n)
    zobrist: int = 0  # Hash para detecção de estados repetidos
    parent: "GameState | None" = None
    move_desc: str = "" 

    @property
    def tableux(self) -> List[StackTuples]:
        return self.stacks[IDX_TABLEAU_START:IDX_TABLEAU_END]
    
    @property
    def foundations(self) -> List[StackTuples]:
        return self.stacks[IDX_FOUNDATION_START:IDX_FOUNDATION_END]
    
    @property
    def stock(self) -> StackTuples:
        return self.stacks[IDX_STOCK]
    
    @property
    def waste(self) -> StackTuples:
        return self.stacks[IDX_WASTE]
    
    def all_stacks(self) -> Iterator[StackTuples]:
        return iter(self.stacks)
    

    def to_tuple(self) -> tuple:
        return tuple(tuple(s) for s in self.stacks)
    
    def foundations_count(self) -> int:
        return sum(len(f) for f in self.foundations)
    
    def hidden_cards_count(self) -> int:
        return sum(1 for tab in self.tableux for _, _, flipped in tab if flipped)
    
    def is_goal(self) -> bool:
        return self.foundations_count() == 52
    
    def __lt__(self, other: "GameState") -> bool:
        return self.f < other.f
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GameState):
            return NotImplemented
        return self.zobrist == other.zobrist
    
    def __hash__(self) -> int:
        return self.zobrist
    
def build_state_from_game(game) -> GameState:
    from zobristHashing import compute_hash

    state = GameState()

    for i, t in enumerate(game.tableaus):
        state.stacks[IDX_TABLEAU_START + i] = [(c.suit, c.symbol, c.flipped) for c in t.cards]

    for i, f in enumerate(game.foundations):
        state.stacks[IDX_FOUNDATION_START + i] = [(c.suit, c.symbol, c.flipped) for c in f.cards]

    state.stacks[IDX_STOCK] = [(c.suit, c.symbol, c.flipped) for c in game.stock.cards]
    state.stacks[IDX_WASTE] = [(c.suit, c.symbol, c.flipped) for c in game.waste.cards]
    state.zobrist = compute_hash(state)

    return state
