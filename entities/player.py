import pygame
import config

class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.radio_nucleo = 4
        self.radio_brillo = 14
        self.color_nucleo = config.COLOR_TEXT
        self.velocidad = 300.0  # Píxeles por segundo

    def actualizar(self, dt, teclas):
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

    def dibujar(self, superficie):
        # 1. Dibujar el halo (brillo transparente)
        surf_brillo = pygame.Surface((self.radio_brillo * 2, self.radio_brillo * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf_brillo, (255, 255, 255, 30), (self.radio_brillo, self.radio_brillo), self.radio_brillo)
        superficie.blit(surf_brillo, (int(self.x) - self.radio_brillo, int(self.y) - self.radio_brillo))
        
        # 2. Dibujar el núcleo sólido
        pygame.draw.circle(superficie, self.color_nucleo, (int(self.x), int(self.y)), self.radio_nucleo)