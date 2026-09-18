import pygame
import config

class LightMask:
    """Crea la niebla de guerra para el laberinto de la Fase 2."""
    def __init__(self):
        self.superficie = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        self.radio_luz = 130 # Qué tan grande es el círculo de visión
        
    def dibujar(self, pantalla, pos_jugador):
        # 1. Llenar toda la superficie de negro completamente opaco
        self.superficie.fill((0, 0, 0, 255))
        
        # 2. Hacer el "agujero" transparente donde está el jugador.
        # Usamos BLEND_RGBA_MIN para restar el color negro en ese círculo.
        pygame.draw.circle(
            self.superficie, 
            (0, 0, 0, 0), 
            (int(pos_jugador[0]), int(pos_jugador[1])), 
            self.radio_luz
        )
        
        # 3. (Opcional) Un borde semitransparente para que la luz se difumine
        pygame.draw.circle(
            self.superficie, 
            (0, 0, 0, 150), 
            (int(pos_jugador[0]), int(pos_jugador[1])), 
            self.radio_luz + 20, 
            20 # Grosor del borde
        )

        # 4. Dibujar la máscara completa sobre el juego
        pantalla.blit(self.superficie, (0, 0))