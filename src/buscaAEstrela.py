from __future__ import annotations

import heapq
import itertools
from typing import List, Tuple, Dict, Optional

from card import Suit, Symbol
from gameState import (
    GameState, build_state_from_game,
    IDX_TABLEAU_START, IDX_TABLEAU_END,
    IDX_FOUNDATION_START, IDX_FOUNDATION_END,
    IDX_STOCK, IDX_WASTE, NUM_STACKS,
    CardTuple, StackTuples,
)
from zobristHashing import update_hash, flip_hash, card_index

_SYMBOL_ORDER = list(Symbol)
_SUIT_LIST    = list(Suit)

PESO_INICIAL = 5

def _symbol_value(symbol: Symbol) -> int:
    return _SYMBOL_ORDER.index(symbol) + 1  # Ás=1 … Rei=13


def _is_red(suit: Suit) -> bool:
    return suit in (Suit.HEARTS, Suit.DIAMONDS)


def heuristica(state: GameState) -> int:
    #Força o algoritmo a odiar cartas ocultas e priorizar revelá-las.
    
    h = 52 - state.foundations_count()

    for tab in state.tableux:
        for depth, (suit, symbol, flipped) in enumerate(tab):
            if flipped:
                h += 1

            if not flipped:
                val = _symbol_value(symbol)
                red = _is_red(suit)
                for depth2, (suit2, symbol2, flipped2) in enumerate(tab):
                    if depth2 >= depth:
                        break
                    if not flipped2 and _is_red(suit2) == red:
                        val2 = _symbol_value(symbol2)
                        if val2 > val:
                            # Penalidade para cartas bloqueadas
                            h += 2

    h += len(state.stock) + len(state.waste)

    return h


def _can_enter_foundation(foundation: StackTuples, suit: Suit, symbol: Symbol) -> bool:
    if not foundation:
        return symbol == Symbol.ACE
    top_suit, top_sym, _ = foundation[-1]
    if top_suit != suit:
        return False
    return _SYMBOL_ORDER.index(symbol) == _SYMBOL_ORDER.index(top_sym) + 1


def _can_enter_tableau(tableau: StackTuples, suit: Suit, symbol: Symbol) -> bool:
    if not tableau:
        return symbol == Symbol.KING
    top_suit, top_sym, top_flipped = tableau[-1]
    if top_flipped:
        return False
    return (_is_red(top_suit) != _is_red(suit) and
            _SYMBOL_ORDER.index(symbol) == _SYMBOL_ORDER.index(top_sym) - 1)


def _clone_stacks(stacks: List[StackTuples]) -> List[StackTuples]:
    return [list(s) for s in stacks]


def _compute_f(g: int, h: int) -> float:
    return g + PESO_INICIAL * h


def _apply_move(state: GameState,
                from_idx: int, to_idx: int,
                amount: int,
                flip_after: bool = False,
                flip_card: Optional[CardTuple] = None,
                flip_depth: Optional[int] = None,
                desc: str = "") -> GameState:

    new_stacks = _clone_stacks(state.stacks)
    new_hash   = state.zobrist

    cards_moved = new_stacks[from_idx][-amount:]
    new_stacks[from_idx] = new_stacks[from_idx][:-amount]

    src_base_depth = len(new_stacks[from_idx])
    dst_base_depth = len(new_stacks[to_idx])

    for i, (suit, symbol, flipped) in enumerate(cards_moved):
        depth_src = src_base_depth + i
        depth_dst = dst_base_depth + i
        new_hash = update_hash(new_hash, suit, symbol,
                               from_idx, depth_src,
                               to_idx,   depth_dst,
                               flipped)

    new_stacks[to_idx].extend(cards_moved)

    if flip_after and new_stacks[from_idx]:
        suit, symbol, flipped = new_stacks[from_idx][-1]
        if flipped:
            depth = len(new_stacks[from_idx]) - 1
            new_hash = flip_hash(new_hash, suit, symbol, from_idx, depth)
            new_stacks[from_idx][-1] = (suit, symbol, False)

    if flip_card is not None and flip_depth is not None:
        suit, symbol, flipped = flip_card
        new_hash = flip_hash(new_hash, suit, symbol, to_idx, flip_depth)
        new_stacks[to_idx][flip_depth] = (suit, symbol, not flipped)

    new_g = state.g + 1
    new_state = GameState(
        stacks    = new_stacks,
        g         = new_g,
        f         = 0,
        zobrist   = new_hash,
        parent    = state,
        move_desc = desc,
    )
    new_h = heuristica(new_state)
    new_state.f = _compute_f(new_g, new_h)
    return new_state


def generate_successors(state: GameState) -> List[GameState]:

    successors: List[GameState] = []

    tab_range   = range(IDX_TABLEAU_START, IDX_TABLEAU_END)
    found_range = range(IDX_FOUNDATION_START, IDX_FOUNDATION_END)

    # Poda de inversão de jogada imediata
    def add_if_not_cycle(ns: GameState):
        if state.parent is not None and ns.zobrist == state.parent.zobrist:
            return
        successors.append(ns)

    # 1. Tableau → Foundation
    for ti in tab_range:
        tab = state.stacks[ti]
        if not tab:
            continue
        suit, symbol, flipped = tab[-1]
        if flipped:
            continue
        for fi in found_range:
            if _can_enter_foundation(state.stacks[fi], suit, symbol):
                ns = _apply_move(state, ti, fi, 1, flip_after=True,
                                 desc=f"T{ti}→F{fi-IDX_FOUNDATION_START} {suit.value}{symbol.value}")
                add_if_not_cycle(ns)
                break

    # 2. Waste → Foundation
    waste = state.stacks[IDX_WASTE]
    if waste:
        suit, symbol, flipped = waste[-1]
        if not flipped:
            for fi in found_range:
                if _can_enter_foundation(state.stacks[fi], suit, symbol):
                    ns = _apply_move(state, IDX_WASTE, fi, 1,
                                     desc=f"W→F{fi-IDX_FOUNDATION_START} {suit.value}{symbol.value}")
                    add_if_not_cycle(ns)
                    break

    # 3. Tableau → Tableau 
    for ti_src in tab_range:
        tab_src = state.stacks[ti_src]
        if not tab_src:
            continue

        face_up: List[CardTuple] = []
        for card in reversed(tab_src):
            if card[2]: 
                break
            face_up.insert(0, card)

        if not face_up:
            continue

        for amount in range(1, len(face_up) + 1):
            bottom_card = face_up[-amount]
            b_suit, b_sym, _ = bottom_card

            for ti_dst in tab_range:
                if ti_dst == ti_src:
                    continue
                if _can_enter_tableau(state.stacks[ti_dst], b_suit, b_sym):
                    ns = _apply_move(state, ti_src, ti_dst, amount, flip_after=True,
                                     desc=f"T{ti_src}→T{ti_dst} ×{amount} {b_suit.value}{b_sym.value}")
                    add_if_not_cycle(ns)

    # 4. Waste → Tableau
    if waste:
        suit, symbol, flipped = waste[-1]
        if not flipped:
            for ti in tab_range:
                if _can_enter_tableau(state.stacks[ti], suit, symbol):
                    ns = _apply_move(state, IDX_WASTE, ti, 1,
                                     desc=f"W→T{ti} {suit.value}{symbol.value}")
                    add_if_not_cycle(ns)

    # 5. Stock → Waste 
    stock = state.stacks[IDX_STOCK]
    if stock:
        suit, symbol, flipped = stock[-1]
        new_stacks = _clone_stacks(state.stacks)
        new_hash   = state.zobrist

        card = new_stacks[IDX_STOCK].pop()
        depth_src = len(new_stacks[IDX_STOCK])
        depth_dst = len(new_stacks[IDX_WASTE])

        new_hash = update_hash(new_hash, suit, symbol,
                               IDX_STOCK, depth_src,
                               IDX_WASTE, depth_dst,
                               True)   
        new_hash = flip_hash(new_hash, suit, symbol, IDX_WASTE, depth_dst)
        new_stacks[IDX_WASTE].append((suit, symbol, False))

        new_g = state.g + 1
        ns = GameState(stacks=new_stacks, g=new_g, zobrist=new_hash,
                       parent=state, move_desc=f"S→W {suit.value}{symbol.value}")
        ns.f = _compute_f(new_g, heuristica(ns))
        add_if_not_cycle(ns)

    # 6. Waste → Stock (Reciclagem)
    elif waste:
        new_stacks = _clone_stacks(state.stacks)
        new_hash   = state.zobrist
        cards_to_move = list(reversed(new_stacks[IDX_WASTE]))
        old_waste_len = len(new_stacks[IDX_WASTE])
        new_stacks[IDX_WASTE] = []
        new_stacks[IDX_STOCK] = []

        for i, (suit, symbol, flipped) in enumerate(cards_to_move):
            new_hash = update_hash(new_hash, suit, symbol,
                                   IDX_WASTE, old_waste_len - 1 - i,
                                   IDX_STOCK, i,
                                   False)   
            new_hash = flip_hash(new_hash, suit, symbol, IDX_STOCK, i)
            new_stacks[IDX_STOCK].append((suit, symbol, True))

        new_g = state.g + 1
        ns = GameState(stacks=new_stacks, g=new_g, zobrist=new_hash,
                       parent=state, move_desc="Reciclar waste→stock")
        ns.f = _compute_f(new_g, heuristica(ns))
        
        # Poda severa: Se o pai do pai foi uma reciclagem exata (ou seja, demos a volta à toa), ignora.
        add_if_not_cycle(ns)

    return successors


class BuscaAEstrela:

    def __init__(self, game, max_states: int = 20_000_000):
        self.game       = game
        self.max_states = max_states
        self.solution_path: Optional[List[str]] = None
        self.found      = False

    def run(self) -> bool:

        initial = build_state_from_game(self.game)
        h0 = heuristica(initial)
        initial.f = _compute_f(initial.g, h0)

        counter   = itertools.count()
        open_heap: List[Tuple[float, int, int, GameState]] = []
        heapq.heappush(open_heap, (initial.f, h0, next(counter), initial))

        best_g: Dict[int, int] = {initial.zobrist: 0}

        closed_count = 0
        log_interval = 1_000

        print(f"Iniciando A* (WA* peso={PESO_INICIAL})...")

        while open_heap:
            if closed_count >= self.max_states:
                print(f"[A*] Limite de estados atingido ({self.max_states:,}). Abortando.")
                return False

            _, _, _, current = heapq.heappop(open_heap)

            if best_g.get(current.zobrist, float("inf")) < current.g:
                continue

            closed_count += 1

            if closed_count % log_interval == 0:
                # Log ajustado para refletir o WA* corretamente
                h_cur = (current.f - current.g) / PESO_INICIAL
                print(f"[A*] Fechados={closed_count:,} Abertos={len(open_heap):,} "
                      f"f={current.f:.2f} g={current.g} h={h_cur:.1f} "
                      f"Fundações={current.foundations_count()}")

            if current.is_goal():
                self.found = True
                self.solution_path = self._reconstruct_path(current)
                print(f"\n[A*] ✓ Solução encontrada em {current.g} movimentos! "
                      f"Fechados={closed_count:,}")
                for step in self.solution_path:
                    print(f"  {step}")
                return True

            for successor in generate_successors(current):
                prev_best = best_g.get(successor.zobrist, float("inf"))
                if successor.g < prev_best:
                    best_g[successor.zobrist] = successor.g
                    h_succ = (successor.f - successor.g) / PESO_INICIAL
                    heapq.heappush(open_heap,
                                   (successor.f, h_succ, next(counter), successor))

        print(f"[A*] Busca concluída sem solução. Fechados={closed_count:,}")
        return False

    @staticmethod
    def _reconstruct_path(state: GameState) -> List[str]:
        path: List[str] = []
        cur = state
        while cur.parent is not None:
            path.append(cur.move_desc)
            cur = cur.parent
        path.reverse()
        return path
