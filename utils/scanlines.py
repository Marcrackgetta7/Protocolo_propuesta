import pygame
import config
from utils.vfx import GradientCache


class Scanlines:
    def __init__(self):
        # Creamos una superficie transparente del tamaño de la pantalla pre-calculada una sola vez
        self.superficie = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)

        # Dibujamos líneas horizontales negras cada 3 píxeles con baja opacidad
        color_linea = (0, 0, 0, 90)
        for y in range(0, config.HEIGHT, 3):
            pygame.draw.line(self.superficie, color_linea, (0, y), (config.WIDTH, y), 1)

        # Añadimos viñeta CRT suave pre-calculada en la misma superficie para un único blit por frame
        vignette = GradientCache.get_vignette(config.WIDTH, config.HEIGHT, strength=95)
        self.superficie.blit(vignette, (0, 0))

    def dibujar(self, pantalla):
        # Se dibuja encima de todo con un único blit
        pantalla.blit(self.superficie, (0, 0))
