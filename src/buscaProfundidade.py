import move
from game import Game
import heapq
import itertools


class BuscaProfundidade():
    def __init__(self, game):
        self.game = game
        self.abertos = []
        self.fechados = []
        self.contador = itertools.count()

    def clone_game_from(self, source):
        clone = Game.__new__(Game)  # evita __init__ que embaralha tudo
        clone.app = source.app
        clone.history = None
        clone.animations = set()
        clone.paused = False
        clone.time = 0
        clone.goal_state = source.goal_state
        clone.profundidade = source.profundidade
        clone.heurisita = 0

        clone.foundations = tuple(f.clone(clone) for f in source.foundations)
        clone.tableaus = tuple(t.clone(clone) for t in source.tableaus)
        clone.waste = source.waste.clone(clone)
        clone.stock = source.stock.clone(clone)
        clone.drag = source.drag.clone(clone)

        clone.clickable_stacks = clone.foundations + clone.tableaus + (clone.stock, clone.waste)
        clone.stacks = (clone.stock, clone.waste) + tuple(reversed(clone.tableaus)) + tuple(reversed(clone.foundations)) + (clone.drag,)

        return clone

    def apply_move(self, m):
        if isinstance(m, move.MoveMove):
            m.redo()
        elif isinstance(m, move.FlipMove):
            m.redo()
        elif isinstance(m, move.ConcurrentMoves):
            for sub in m.moves:
                self.apply_move(sub)
        elif isinstance(m, move.SequentialMoves):
            for sub in m.moves:
                self.apply_move(sub)

    def get_filhos(self, game_atual):
        filhos = []
        possiveis_movimentos = game_atual.get_possible_moves(game_atual.get_state())

        for origem, destino in possiveis_movimentos:
            clone = self.clone_game_from(game_atual)
            clone.profundidade = game_atual.profundidade + 1

            pilha_origem = next((s for s in clone.stacks if s.pos == origem.pos), None)
            pilha_destino = next((s for s in clone.stacks if s.pos == destino.pos), None)

            if not pilha_origem or not pilha_destino or pilha_origem.is_empty:
                continue

            # Determina quantas cartas (com face para cima) mover do topo
            amount = 1
            if pilha_origem.size > 1:
                cartas_mover = []
                for card in reversed(pilha_origem.cards):
                    if not card.flipped:
                        cartas_mover.insert(0, card)
                    else:
                        break
                amount = len(cartas_mover) if cartas_mover else 1

            movimento_objeto = move.MoveMove(pilha_origem, pilha_destino, amount)
            self.apply_move(movimento_objeto)

            # Revela automaticamente a carta que ficou exposta no topo da origem
            if not pilha_origem.is_empty and pilha_origem.card_on_top.flipped:
                pilha_origem.card_on_top.flip()

            clone.heurisita = clone.define_heuristica()
            filhos.append(clone)

        filhos.sort(key=lambda x: x.heurisita, reverse=True)
        return filhos

    def busca_profundidade(self, estado_inicial=None):
        estado_inicial = self.clone_game_from(self.game)
        estado_inicial.profundidade = 0
        estado_inicial.heurisita = estado_inicial.define_heuristica()

        # heapq é min-heap, então usamos -heurística para simular max-heap
        abertos = [(-estado_inicial.heurisita, next(self.contador), estado_inicial)]
        visitados = set()
        fechados = 0

        print("Iniciando Busca Melhor-Primeiro...")

        while abertos:
            _, _, game_atual = heapq.heappop(abertos)
            estado_tupla = game_atual.get_state()

            if estado_tupla in visitados:
                continue

            visitados.add(estado_tupla)
            fechados += 1

            if fechados % 50 == 0:
                print(f"Profundidade: {game_atual.profundidade}, Heurística: {game_atual.heurisita}, "
                      f"Abertos: {len(abertos)}, Fechados: {fechados}")

            if game_atual.is_goal_state(estado_tupla):
                print("Solução encontrada!")
                return True

            if game_atual.profundidade >= 500:
                continue

            for filho in self.get_filhos(game_atual):
                heapq.heappush(abertos, (-filho.heurisita, next(self.contador), filho))

        print(f"Busca concluída. Não encontrou solução. Fechados: {fechados}")
        return False