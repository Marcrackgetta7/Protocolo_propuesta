import math
import random
import pygame
import config
from entities.particle import Particle
from utils.vfx import GlowCache


class Anomaly:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radio = 8
        self.color = config.COLOR_ENERGY  # Rosa oscuro / ki Rosé
        self.particulas = []
        self.recolectada = False
        self.tiempo = random.uniform(0.0, math.tau)

    def actualizar(self, dt):
        self.tiempo += dt
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
            cx, cy = int(self.x), int(self.y)
            pulso = 1.0 + 0.2 * math.sin(self.tiempo * 5.0)

            # Halo energético aditivo pre-cacheado
            GlowCache.blit(superficie, cx, cy, int(self.radio * 3.0 * pulso), self.color, intensity=0.75)

            # Anillo exterior giratorio (rombo energético)
            r_ext = self.radio + 5
            pts = [
                (cx + math.cos(self.tiempo * 2.5 + i * math.pi / 2) * r_ext,
                 cy + math.sin(self.tiempo * 2.5 + i * math.pi / 2) * r_ext)
                for i in range(4)
            ]
            pygame.draw.polygon(superficie, (255, 150, 200), pts, 1)

            # Núcleo de cristal y centro incandescente
            pygame.draw.circle(superficie, self.color, (cx, cy), self.radio)
            pygame.draw.circle(superficie, (255, 235, 245), (cx, cy), max(2, int(self.radio * 0.45 * pulso)))
