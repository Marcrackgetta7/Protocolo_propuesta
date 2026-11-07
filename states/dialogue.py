import math
import pygame
from utils.fonts import get_font
from states.base_state import BaseState
from utils.text_renderer import TypewriterText
from utils.vfx import GlowCache, GradientCache, FloatingParticles, ProceduralUI
import config


class Dialogue(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "PROPOSAL"  # Al terminar, pasa a la gran pregunta

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
        self.tiempo = 0.0
        self.fuente_hint = get_font(15)
        self.bg_surf = GradientCache.get_vertical(
            config.WIDTH, config.HEIGHT, (10, 6, 18), (22, 8, 20), vignette=True
        )
        self.particulas = FloatingParticles(count=35, mode="romantic")
        self.panel_rect = pygame.Rect(35, config.HEIGHT // 2 - 65, config.WIDTH - 70, 150)

    def startup(self):
        self.indice_mensaje = 0
        self.tiempo = 0.0
        self.mostrar_mensaje_actual()

    def mostrar_mensaje_actual(self):
        texto = self.mensajes[self.indice_mensaje]
        self.escritor = TypewriterText(
            self.font, texto, (55, config.HEIGHT // 2 - 25), speed=0.04, max_width=config.WIDTH - 110
        )

    def manejar_eventos(self, evento):
        if (evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE) or evento.type == pygame.MOUSEBUTTONDOWN:
            if self.escritor.finished:
                # Si el texto terminó, pasamos al siguiente
                self.indice_mensaje += 1
                if self.indice_mensaje < len(self.mensajes):
                    self.mostrar_mensaje_actual()
                else:
                    self.done = True  # Terminan los diálogos, pasa a la Fase 3
            else:
                # Si está escribiendo, lo mostramos completo instantáneamente
                self.escritor.index = len(self.escritor.text)
                self.escritor.current_text = self.escritor.text
                self.escritor.finished = True

    def actualizar(self, dt):
        self.tiempo += dt
        self.particulas.update(dt)
        if self.escritor:
            self.escritor.actualizar(dt)

    def dibujar(self, superficie):
        superficie.blit(self.bg_surf, (0, 0))
        self.particulas.draw(superficie)

        ProceduralUI.draw_panel(
            superficie, self.panel_rect,
            bg_color=(16, 10, 24, 215),
            border_color=config.COLOR_ENERGY,
            cut=14,
            glow=True
        )

        for i in range(len(self.mensajes)):
            nx = self.panel_rect.left + 28 + i * 18
            ny = self.panel_rect.bottom - 18
            activo = (i == self.indice_mensaje)
            col = config.COLOR_ENERGY if activo else (80, 75, 95)
            pygame.draw.circle(superficie, col, (nx, ny), 4 if activo else 3)

        if self.escritor:
            self.escritor.dibujar(superficie)
            if self.escritor.finished:
                pulso = 0.55 + 0.45 * math.sin(self.tiempo * 5.5)
                c_hint = (int(240 * pulso), int(160 * pulso), int(200 * pulso))
                hint = self.fuente_hint.render("[ ESPACIO / CLIC PARA CONTINUAR ]", True, c_hint)
                superficie.blit(hint, (self.panel_rect.right - hint.get_width() - 24, self.panel_rect.bottom - 26))
