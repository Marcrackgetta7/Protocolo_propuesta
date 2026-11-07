import math
import pygame
import config
from utils.vfx import GlowCache, TrailRenderer


class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.radio_nucleo = 4
        self.radio_brillo = 14
        self.color_nucleo = config.COLOR_TEXT
        self.velocidad = 300.0  # Píxeles por segundo
        self.trail = TrailRenderer(max_points=10)
        self.tiempo = 0.0

    def actualizar(self, dt, teclas):
        self.tiempo += dt
        dx, dy = 0, 0
        # Movimiento con flechas o WASD
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            dy -= 1
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            dy += 1
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            dx -= 1
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            dx += 1

        # Normalizar vector para que no se mueva más rápido en diagonal
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        self.x += dx * self.velocidad * dt
        self.y += dy * self.velocidad * dt

        # Limitar colisiones a los bordes de la pantalla
        self.x = max(self.radio_brillo, min(config.WIDTH - self.radio_brillo, self.x))
        self.y = max(self.radio_brillo, min(config.HEIGHT - self.radio_brillo, self.y))

        self.trail.add(self.x, self.y)

    def dibujar(self, superficie):
        # Si el estado mueve x/y manualmente (como Maze), registramos la estela también
        self.trail.add(self.x, self.y)
        self.trail.draw(superficie, (160, 210, 255), base_radius=5)

        t = pygame.time.get_ticks() * 0.005
        pulso = 1.0 + 0.14 * math.sin(t)
        px, py = int(self.x), int(self.y)

        # 1. Halo pre-cacheado con BLEND_RGB_ADD (sin crear Surface por frame)
        GlowCache.blit(superficie, px, py, int(self.radio_brillo * 1.45 * pulso), (180, 220, 255), intensity=0.55)

        # 2. Anillo orbital sutil
        r_anillo = int(self.radio_nucleo + 5 + math.sin(t * 1.5) * 1.5)
        pygame.draw.circle(superficie, (160, 200, 255), (px, py), r_anillo, 1)

        # 3. Dos nodos orbitales
        for i in range(2):
            ang = t * 1.8 + i * math.pi
            ox = px + int(math.cos(ang) * (r_anillo + 2))
            oy = py + int(math.sin(ang) * (r_anillo + 2))
            pygame.draw.circle(superficie, (255, 255, 255), (ox, oy), 1)

        # 4. Núcleo sólido brillante
        pygame.draw.circle(superficie, self.color_nucleo, (px, py), self.radio_nucleo)
