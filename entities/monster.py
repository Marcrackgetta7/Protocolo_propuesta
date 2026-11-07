import math
import random
import pygame
from entities.particle import Particle
from utils.vfx import GlowCache
import config


class Monster:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.radio = 15
        self.velocidad = 70.0  # Moderadamente reducida para permitir maniobrar y hackear terminales
        self.particulas = []
        self.angulo = random.uniform(0.0, math.tau)

    def actualizar(self, dt, jugador_x, jugador_y):
        self.angulo += 3.2 * dt
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

        cx, cy = int(self.x), int(self.y)
        GlowCache.blit(superficie, cx, cy, self.radio * 2, config.COLOR_DANGER, intensity=0.65)

        # Corona dentada corrupta giratoria
        pts = []
        num_puntas = 8
        for i in range(num_puntas * 2):
            ang = self.angulo + (i * math.pi / num_puntas)
            r = (self.radio + 4) if i % 2 == 0 else (self.radio - 3)
            pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
        pygame.draw.polygon(superficie, (180, 0, 0), pts)
        pygame.draw.polygon(superficie, (255, 80, 80), pts, 1)

        # Núcleo oscuro abisal y pupila carmesí
        pygame.draw.circle(superficie, (30, 0, 5), (cx, cy), self.radio - 5)
        pygame.draw.circle(superficie, (255, 50, 50), (cx, cy), 4)
