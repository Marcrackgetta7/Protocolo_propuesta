import pygame
import random
import config
from entities.particle import Particle

class Anomaly:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radio = 8
        self.color = config.COLOR_ENERGY # Rosa oscuro / ki Rosé
        self.particulas = []
        self.recolectada = False

    def actualizar(self, dt):
        # Generar nuevas partículas para el aura si no ha sido recolectada
        if not self.recolectada and random.random() < 0.3:
            self.particulas.append(Particle(self.x, self.y, self.color))
        
        # Actualizar las partículas vivas
        for p in self.particulas[:]:
            p.actualizar(dt)
            if p.vida <= 0 or p.tamaño <= 0:
                self.particulas.remove(p)

    def dibujar(self, superficie):
        for p in self.particulas:
            p.dibujar(superficie)
        
        if not self.recolectada:
            pygame.draw.circle(superficie, self.color, (int(self.x), int(self.y)), self.radio)