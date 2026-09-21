import pygame
import random

class Particle:
    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        # Velocidad aleatoria en todas las direcciones
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.tamaño = random.randint(3, 6)
        self.vida = 255 # Transparencia alfa
        self.velocidad_decaimiento = random.uniform(3, 7)

    def actualizar(self, dt):
        # Ajustamos el movimiento con el Delta Time
        self.x += self.vx * 60 * dt
        self.y += self.vy * 60 * dt
        self.vida -= self.velocidad_decaimiento * 60 * dt
        self.tamaño -= 0.1 * 60 * dt

    def dibujar(self, superficie):
        if int(self.tamaño) > 0 and self.vida > 0:
            surf = pygame.Surface((int(self.tamaño), int(self.tamaño)))
            surf.fill(self.color)
            # El modo de fusión BLEND_ADD para el efecto de luz y energía
            superficie.blit(surf, (int(self.x), int(self.y)), special_flags=pygame.BLEND_ADD)