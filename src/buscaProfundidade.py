import pygame

import assets
import constants
from game import Game
from ui import UI, UIType

class BuscaProfundidade():
    def __init__(self, game):
        self.game = game
        self.abertos = set()
        self.fechados = []
    
    def busca_profundidade(self, state):
        if state in self.abertos:
            return False
        
        self.abertos.add(state)

        if self.game.is_goal_state(state):
            return True
        
        for move in self.game.get_possible_moves(state):
            new_state = self.game.apply_move(state, move)
            if self.busca_profundidade(new_state):
                self.fechados.append(move)
                return True
        
        return False
    
    def DFS(init):
        abertos = [init]
        fechados = []
        objetivo = [[1,2,3], [8,0,4], [7,6,5]]
        iteracoes = 0
        profundidade = 0

        while abertos:
            no = abertos.pop(0)
            profundidade = contarProfundidade(no)
            #print("No atual: " + str(no.matriz))
            if no.matriz == objetivo:
                print("Numero de iterações: " + str(iteracoes))
                return no
            elif profundidade < 5:  # Limitar a profundidade máxima
                no.filhos = gerarFilhos(no)
                fechados.append(no)
                if no.filhos:
                    for filho in no.filhos:
                        matrizFilho = filho.matriz
                        for matrizAberta in abertos:
                            if matrizFilho == matrizAberta.matriz:
                                break
                        for matrizFechada in fechados:
                            if matrizFilho == matrizFechada.matriz:
                                break
                        else:
                            abertos.insert(0, filho)
            iteracoes += 1
        
        return None
    
    def contarProfundidade(no):
        profundidade = 0
        while no.pai is not None:
            no = no.pai
            profundidade += 1
        return profundidade
    
    def gerarFilhos(estado):
        pass
        return 

