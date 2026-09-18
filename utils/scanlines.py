import pygame
import config

class Scanlines:
    def __init__(self):
        # Creamos una superficie transparente del tamaño de la pantalla
        self.superficie = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        
        # Dibujamos líneas horizontales negras cada 3 píxeles con baja opacidad
        color_linea = (0, 0, 0, 100) # Negro con 100 de Alpha (transparencia)
        for y in range(0, config.HEIGHT, 3):
            pygame.draw.line(self.superficie, color_linea, (0, y), (config.WIDTH, y), 1)

    def dibujar(self, pantalla):
        # Se dibuja encima de todo
        pantalla.blit(self.superficie, (0, 0))