import pygame
from states.base_state import BaseState
from utils.text_renderer import TypewriterText
from utils import audio
import config

class Interlude(BaseState):
    def __init__(self, mensajes, next_state):
        super().__init__()
        self.next_state = next_state
        self.mensajes = mensajes
        self.indice_mensaje = 0
        self.escritor = None

    def startup(self):
        self.indice_mensaje = 0
        self.mostrar_mensaje_actual()

    def mostrar_mensaje_actual(self):
        texto = self.mensajes[self.indice_mensaje]
        self.escritor = TypewriterText(self.font, texto, (50, config.HEIGHT // 2), speed=0.04)

    def manejar_eventos(self, evento):
        if (evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE) or evento.type == pygame.MOUSEBUTTONDOWN:
            if self.escritor.finished:
                self.indice_mensaje += 1
                if self.indice_mensaje < len(self.mensajes):
                    self.mostrar_mensaje_actual()
                else:
                    self.done = True 
            else:
                # Si adelanta el texto de golpe...
                self.escritor.index = len(self.escritor.text)
                self.escritor.current_text = self.escritor.text
                self.escritor.finished = True
                # ...Callamos el tecleo de inmediato para que no se quede sonando
                audio.detener_sonido("tecla")

    def actualizar(self, dt):
        if self.escritor:
            self.escritor.actualizar(dt)

    def dibujar(self, superficie):
        superficie.fill(config.COLOR_BG)
        if self.escritor:
            self.escritor.dibujar(superficie)