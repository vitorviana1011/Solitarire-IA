import pygame

import assets
import constants
import move
from game import Game
from ui import UI, UIType

class BuscaProfundidade():
    def __init__(self, game):
        self.game = game
        self.abertos = set()
        self.fechados = []
        self.caminho = []
    
    # Clona o estado atual do jogo para criar um novo estado a partir dele
    def clone_game(self):
        clone = Game(self.game.app)
        clone.stacks = [s.clone(clone) for s in self.game.stacks]
        clone.foundations = [f.clone(clone) for f in self.game.foundations]
        clone.stock = clone.stacks[0]
        clone.profundidade = self.game.profundidade + 1 if self.game.profundidade is not None else 0
        return clone
    
    # Aplica o movimento no jogo clonado, verificando o tipo do movimento para aplicar a função correta
    def apply_move(self, move):
        if isinstance(move, move.MoveMove):
            move.redo()
        elif isinstance(move, move.FlipMove):
            move.redo()
        elif isinstance(move, move.ConcurrentMoves):
            for m in move.moves:
                m.redo()
        elif isinstance(move, move.SequentialMoves):
            for m in move.moves:
                m.redo()
    
    # Gera os estados filhos a partir do estado atual, aplicando todos os movimentos possíveis
    def get_filhos(self, game_atual):
        filhos = []
        for move in game_atual.get_possible_moves(game_atual.get_state()):
            clone = self.clone_game()
            clone.profundidade = game_atual.profundidade + 1 if game_atual.profundidade is not None else 0
            self.apply_move(move)
            filhos.append(clone)

        filhos.sort(key=lambda x: self.game.define_heuristica(x), reverse=True) # Ordena os filhos pela heurística, para priorizar os estados mais promissores

        return filhos
    
    def execute_solution(self, historico):
        pass
    
    def busca_profundidade(self):
        self.abertos.add(self.clone_game()) # Adiciona o estado inicial à lista de abertos
        historico = []
        visitados = set() # Guarda apenas as tuplas, otimizando a verificação de estados já visitados

        while self.abertos:
            game_atual = self.abertos.pop()
            estado_tupla = game_atual.get_state()

            if self.game.is_goal_state(estado_tupla):
                historico = game_atual.get_history() # Recupera o histórico de movimentos para chegar ao estado objetivo
                self.execute_solution(historico)
                return True
            
            if game_atual.profundidade >= 200: # Limite de profundidade para evitar loops infinitos
                print("Limite de profundidade atingido, abortando busca em profundidade")
                continue

            if estado_tupla in visitados:
                continue

            visitados.add(estado_tupla)
            self.fechados.append(game_atual)
            
            filhos = self.get_filhos(game_atual)
            self.fechados.append(game_atual)
            for filho in filhos:
                if filho not in self.abertos and filho not in self.fechados:
                    self.abertos.add(filho)
        return False

