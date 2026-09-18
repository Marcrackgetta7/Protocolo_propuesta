import pygame
from states.base_state import BaseState
import config

class Outro(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "OUTRO"

    def manejar_eventos(self, evento):
        # Permite cerrar el juego con Escape o la X de la ventana
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self.quit = True 

    def dibujar(self, superficie):
        superficie.fill(config.COLOR_BG)
        # Aquí puedes cambiar el mensaje final
        texto = self.font.render("SISTEMA RESTAURADO <3. CIERRA LA VENTANA.", True, config.COLOR_ENERGY)
        texto_rect = texto.get_rect(center=(config.WIDTH//2, config.HEIGHT//2))
        superficie.blit(texto, texto_rect)