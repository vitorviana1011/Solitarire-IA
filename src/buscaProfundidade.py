import move
from game import Game


class BuscaProfundidade():
    def __init__(self, game):
        self.game = game
        self.abertos = []
        self.fechados = []

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

            # Calcula quantas cartas mover (topo virado = 1, grupo = várias)
            amount = origem.cont_flipped_cards() if hasattr(origem, 'cont_flipped_cards') else 1
            amount = max(1, min(amount, pilha_origem.size))

            movimento_objeto = move.MoveMove(pilha_origem, pilha_destino, amount)
            self.apply_move(movimento_objeto)

            clone.heurisita = clone.define_heuristica()
            filhos.append(clone)

        filhos.sort(key=lambda x: x.heurisita, reverse=True)
        return filhos

    def busca_profundidade(self):
        estado_inicial = self.clone_game_from(self.game)
        estado_inicial.profundidade = 0
        self.abertos = [estado_inicial]
        visitados = set()
        self.fechados = []

        print("Iniciando Busca em Profundidade...")

        while self.abertos:
            game_atual = self.abertos.pop()
            estado_tupla = game_atual.get_state()

            if estado_tupla in visitados:
                continue

            visitados.add(estado_tupla)
            self.fechados.append(estado_tupla)

            print(f"Profundidade: {game_atual.profundidade}, Heurística: {game_atual.heurisita}, "
                  f"Abertos: {len(self.abertos)}, Fechados: {len(self.fechados)}")

            if game_atual.is_goal_state(estado_tupla):
                print("Solução encontrada!")
                return True

            if game_atual.profundidade >= 200:
                continue

            for filho in self.get_filhos(game_atual):
                self.abertos.append(filho)

        print("Busca em profundidade concluída. Não encontrou solução.")
        return False