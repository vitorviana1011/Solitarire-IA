from collections import deque
from random import shuffle

import constants
from animation import Animation
from card import Card, Suit, Symbol
from history import History
from move import ConcurrentMoves, FlipMove, Move, MoveMove, SequentialMoves
from stack import DragStack, FoundationStack, Stack, StockStack, TableauStack, WasteStack


class Game():
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.history = History(self)
        self.animations: set[Animation] = set()
        self.deck = self.create_deck()
        shuffle(self.deck)
        self.setup_stacks()
        self.deal()
        self.paused = False
        self.time = 0
        self.goal_state = tuple((s, symbol) for s in Suit for symbol in Symbol) # Objetivo é ter as 52 cartas nas fundações, em ordem crescente, começando com o Ás
        self.profundidade = None
        self.table_goal_state = tuple((c.suit, c.symbol) for f in self.foundations for c in f.cards) # O estado do jogo é representado pelas cartas presentes nas fundações, em ordem crescente
        self.heurisita = 0
        self.ai_moves_queue = []

    def create_deck(self):
        return deque(Card(self.app, suit, symbol) for symbol in Symbol for suit in Suit)

    def setup_stacks(self):
        self.foundations = tuple(FoundationStack(self.app, (i*constants.CARD_WIDTH_MARGIN + constants.BIG_MARGIN, constants.BIG_MARGIN)) for i in range(4))
        self.waste = WasteStack(self.app, (4*constants.CARD_WIDTH_MARGIN + constants.BIG_MARGIN, constants.BIG_MARGIN))
        self.stock = StockStack(self.app, (6*constants.CARD_WIDTH_MARGIN + constants.BIG_MARGIN, constants.BIG_MARGIN))
        self.tableaus = tuple(TableauStack(self.app, (i*constants.CARD_WIDTH_MARGIN + constants.BIG_MARGIN, constants.CARD_HEIGHT_MARGIN + constants.BIG_MARGIN)) for i in range(7))
        self.drag = DragStack(self.app, (0, 0))
        self.clickable_stacks: tuple[Stack] = self.foundations + self.tableaus + (self.stock, self.waste)
        self.stacks: tuple[Stack] = (self.stock, self.waste) + tuple(reversed(self.tableaus)) + tuple(reversed(self.foundations)) + (self.drag,)

    def deal(self):
        self.stock.cards = self.deck
        self.stock.reset_pos()
        moves = []
        k = 1
        for i, stack in enumerate(self.tableaus):
            for j in range(i+1):
                m = MoveMove(self.stock, stack, 1)
                if i == j:
                    m = ConcurrentMoves((m, FlipMove(self.stock.cards[-k])))
                moves.append(m)
                k += 1

        self.animations.add(SequentialMoves(moves).redo())

    def undo(self):
        if self.paused:
            return

        self.cancel_animations()
        self.history.undo()

    def redo(self):
        if self.paused:
            return

        self.cancel_animations()
        self.history.redo()

    def deal_card(self):
        if self.paused:
            return

        self.cancel_animations()
        if self.stock.is_empty:
            self.history.add_move(ConcurrentMoves(tuple(FlipMove(c) for c in self.waste.cards) + (MoveMove(self.waste, self.stock, self.waste.size, True),)))
        else:
            self.history.add_move(ConcurrentMoves((FlipMove(self.stock.card_on_top), MoveMove(self.stock, self.waste, 1))))

    def _collect_card_move(self, stack: Stack, foundation: FoundationStack) -> Move:
        move = MoveMove(stack, foundation, 1)
        if len(stack.cards) > 1 and stack.cards[-2].flipped:
            move = ConcurrentMoves((FlipMove(stack.cards[-2]), move))
        return move

    def collect_card(self, stack: Stack):
        if stack.is_empty:
            return

        for f in self.foundations:
            if f.can_enter(stack.card_on_top, 1):
                self.cancel_animations()
                self.history.add_move(self._collect_card_move(stack, f))
                return

    def collect_all(self):
        if self.paused:
            return

        self.cancel_animations()
        moves = []
        b = True
        while b:
            b = False
            for stack in self.tableaus + (self.waste,):
                for f in self.foundations:
                    if not stack.is_empty and f.can_enter(stack.card_on_top, 1):
                        move = self._collect_card_move(stack, f)
                        moves.append(move)
                        move.redo()
                        b = True
                        continue
        if moves:
            m = SequentialMoves(moves)
            list(m.undo().animations)
            self.history.add_move(m)

    def cancel_animations(self):
        if self.paused:
            return

        for animation in self.animations:
            animation.cancel()

    def pause(self):
        self.paused = not self.paused
    # endregion

    def draw(self, screen):
        if not self.paused:
            for animation in set(self.animations):
                animation.tick(self.app.clock.get_time())
                if animation.done:
                    self.animations.remove(animation)

            if not self.animations and hasattr(self, 'ai_moves_queue') and self.ai_moves_queue:
                next_move_str = self.ai_moves_queue.pop(0)
                self.execute_ai_move(next_move_str)

            if not self.animations and all(f.size == 13 for f in self.foundations):
                print("WIN")
                self.app.game_win()
            else:
                self.time += self.app.clock.get_time()

        for stack in self.stacks:
            stack.draw(screen)

    # region Mouse
    def clicked_stack(self, pos):
        for s in self.clickable_stacks:
            if s.rect.collidepoint(pos):
                return s

    def on_mouseclick_l(self, pos):
        if self.paused:
            return

        if self.clicked_stack(pos) == self.stock:
            self.deal_card()

    def on_mouseclick_m(self, pos):
        if self.paused:
            return

        s = self.clicked_stack(pos)
        if s and s.get_cards_to_drag(pos) == 1:
            self.collect_card(s)
        else:
            self.collect_all()

    def on_mousedrag_l(self, pos):
        if self.paused:
            return

        self.drag.mouse_pos = pos

    def on_mousedragbegin_l(self, pos):
        if self.paused:
            return

        for s in self.stacks:
            c = s.get_cards_to_drag(pos)
            if c:
                self.cancel_animations()
                self.drag.cards += list(s.cards)[s.size-c:]
                self.drag.source_stack = s
                self.drag.offset = (pos[0] - self.drag.cards[0].pos[0], pos[1] - self.drag.cards[0].pos[1])

    def on_mousedragend_l(self, pos):
        if self.paused:
            return

        if self.drag.is_empty:
            return

        for s in self.stacks:
            if s.rect.collidepoint(pos) and s.can_enter(self.drag.card_on_bottom, self.drag.size):
                move = MoveMove(self.drag.source_stack, s, self.drag.size)
                if self.drag.source_stack in self.tableaus and self.drag.source_stack.size > self.drag.size and self.drag.source_stack.cards[-self.drag.size-1].flipped:
                    move = ConcurrentMoves((FlipMove(self.drag.source_stack.cards[-self.drag.size-1]), move))
                self.history.add_move(move)
                break

        self.drag.cards.clear()
        self.animations.add(self.drag.source_stack.animate())
    # endregion

    def execute_ai_move(self, desc: str):
        from move import MoveMove, ConcurrentMoves, FlipMove

        # Se for comprar carta ou reciclar o lixo, a própria mecânica de deal_card cuida das animações e viradas
        if desc.startswith("S→W") or desc.startswith("Reciclar"):
            self.deal_card()
            return
        
        # Faz o parse da string gerada pelo BuscaAEstrela (ex: "T3→F0", "W→T2", "T1→T2 ×3")
        parts = desc.split(" ")
        action = parts[0]
        origem_str, destino_str = action.split("→")
        
        # Mapeia a Origem
        if origem_str == "W":
            origem_stack = self.waste
        elif origem_str.startswith("T"):
            origem_stack = self.tableaus[int(origem_str[1:])]
            
        # Mapeia o Destino
        if destino_str.startswith("F"):
            destino_stack = self.foundations[int(destino_str[1:])]
        elif destino_str.startswith("T"):
            destino_stack = self.tableaus[int(destino_str[1:])]
            
        # Pega a quantidade de cartas a mover
        amount = 1
        if "×" in desc:
            for p in parts:
                if p.startswith("×"):
                    amount = int(p[1:])
                    break
                    
        move = MoveMove(origem_stack, destino_stack, amount)
        
        # Se estamos tirando uma carta de um Tableau e a próxima que sobrou lá estiver virada para baixo, 
        # aciona o Flip (virar) junto com o movimento
        if origem_stack in self.tableaus and origem_stack.size > amount and origem_stack.cards[-amount-1].flipped:
            move = ConcurrentMoves((FlipMove(origem_stack.cards[-amount-1]), move))
            
        self.history.add_move(move)

    def __str__(self):
        res = f"--- Estado do Jogo (Profundidade: {self.profundidade}) ---\n"
        res += f"Foundations: {[len(f.cards) for f in self.foundations]}\n"
        res += f"Tableaus (topos): {[t.cards[-1] if t.cards else 'Vazio' for t in self.tableaus]}\n"
        res += "-----------------------------------"
        return res
