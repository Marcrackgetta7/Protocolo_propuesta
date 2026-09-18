import pygame
from states.base_state import BaseState
from utils.text_renderer import TypewriterText
import config

class Dialogue(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "PROPOSAL" # Al terminar, pasa a la gran pregunta
        
        # Aquí puedes modificar los textos exactamente a tu gusto
        self.mensajes = [
            "> DESENCRIPTANDO FRAGMENTOS DE MEMORIA...",
            "> ANOMALÍA 01: Archivos de casi 3 años de amistad recuperados.",
            "> ANOMALÍA 02: Advertencia. Niveles críticos de cafeína en el sistema.",
            "> ANOMALÍA 03: Alerta de intrusión... Entidad 'enano' detectada.",
            "> INTERVENCIÓN COMPLETADA. Limpiando pantalla..."
        ]
        self.indice_mensaje = 0
        self.escritor = None

    def startup(self):
        self.indice_mensaje = 0
        self.mostrar_mensaje_actual()

    def mostrar_mensaje_actual(self):
        texto = self.mensajes[self.indice_mensaje]
        self.escritor = TypewriterText(self.font, texto, (50, config.HEIGHT // 2), speed=0.04)

    def manejar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE or evento.type == pygame.MOUSEBUTTONDOWN:
            if self.escritor.finished:
                # Si el texto terminó, pasamos al siguiente
                self.indice_mensaje += 1
                if self.indice_mensaje < len(self.mensajes):
                    self.mostrar_mensaje_actual()
                else:
                    self.done = True # Terminan los diálogos, pasa a la Fase 3
            else:
                # Si está escribiendo, lo mostramos completo instantáneamente
                self.escritor.index = len(self.escritor.text)
                self.escritor.current_text = self.escritor.text
                self.escritor.finished = True

    def actualizar(self, dt):
        if self.escritor:
            self.escritor.actualizar(dt)

    def dibujar(self, superficie):
        superficie.fill(config.COLOR_BG)
        if self.escritor:
            self.escritor.dibujar(superficie)