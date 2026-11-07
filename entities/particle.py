import random
from utils.vfx import GlowCache


class Particle:
    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        # Velocidad aleatoria en todas las direcciones
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.tamaño = random.randint(3, 6)
        self.vida = 255  # Transparencia alfa
        self.velocidad_decaimiento = random.uniform(3, 7)

    def actualizar(self, dt):
        # Ajustamos el movimiento con el Delta Time
        self.x += self.vx * 60 * dt
        self.y += self.vy * 60 * dt
        self.vida -= self.velocidad_decaimiento * 60 * dt
        self.tamaño -= 0.1 * 60 * dt

    def dibujar(self, superficie):
        tam = int(self.tamaño)
        if tam > 0 and self.vida > 0:
            # Usa GlowCache pre-calculado en lugar de instanciar pygame.Surface por frame
            ratio_vida = max(0.1, min(1.0, self.vida / 255.0))
            GlowCache.blit(superficie, self.x, self.y, max(2, tam * 2), self.color, intensity=0.8 * ratio_vida)
