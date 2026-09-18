import pygame
from states.base_state import BaseState
from utils.text_renderer import TypewriterText
import config

class Intro(BaseState):
    def __init__(self):
        super().__init__()
        # ¡AQUÍ ESTÁ EL CAMBIO! Ahora dirige al minijuego
        self.next_state = "MINIGAME" 
        self.escritor = None 

    def startup(self):
        mensaje = "> INICIANDO PROTOCOLO: BRECHA... PRESIONA ESPACIO PARA SALTAR"
        self.escritor = TypewriterText(self.font, mensaje, (50, config.HEIGHT // 2), speed=0.05)

    def manejar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                self.done = True 
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            self.done = True

    def actualizar(self, dt):
        if self.escritor:
            self.escritor.actualizar(dt)

    def dibujar(self, superficie):
        superficie.fill(config.COLOR_BG)
        if self.escritor:
            self.escritor.dibujar(superficie)