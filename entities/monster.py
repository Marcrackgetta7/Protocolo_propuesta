import pygame
import math
import random
from entities.particle import Particle
import config

class Monster:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.radio = 15
        self.velocidad = 100.0 # Más lento que el jugador para que pueda escapar
        self.particulas = []
        
    def actualizar(self, dt, jugador_x, jugador_y):
        # Perseguir al jugador sin descanso
        dx = jugador_x - self.x
        dy = jugador_y - self.y
        distancia = math.hypot(dx, dy)
        
        if distancia > 0:
            self.x += (dx / distancia) * self.velocidad * dt
            self.y += (dy / distancia) * self.velocidad * dt
            
        # Efecto visual de inestabilidad soltando partículas rojas
        if random.random() < 0.4:
            self.particulas.append(Particle(self.x, self.y, config.COLOR_DANGER))
            
        for p in self.particulas[:]:
            p.actualizar(dt)
            if p.vida <= 0 or p.tamaño <= 0:
                self.particulas.remove(p)

    def dibujar(self, superficie):
        for p in self.particulas:
            p.dibujar(superficie)
        pygame.draw.circle(superficie, (180, 0, 0), (int(self.x), int(self.y)), self.radio)