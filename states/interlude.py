import math
import pygame
from utils.fonts import get_font
from states.base_state import BaseState
from utils.text_renderer import TypewriterText
from utils import audio
from utils.vfx import GlowCache, GradientCache, FloatingParticles, ProceduralUI
import config


class Interlude(BaseState):
    def __init__(self, mensajes, next_state):
        super().__init__()
        self.next_state = next_state
        self.mensajes = mensajes
        self.indice_mensaje = 0
        self.escritor = None
        self.tiempo = 0.0
        self.fuente_hint = get_font(15)
        self.bg_surf = GradientCache.get_vertical(
            config.WIDTH, config.HEIGHT, (8, 10, 18), (14, 8, 16), vignette=True
        )
        self.particulas = FloatingParticles(count=28, mode="cyber")
        self.panel_rect = pygame.Rect(40, config.HEIGHT // 2 - 75, config.WIDTH - 80, 165)

    def startup(self):
        self.done = False
        audio.detener_musica()
        self.indice_mensaje = 0
        self.tiempo = 0.0
        self.mostrar_mensaje_actual()

    def mostrar_mensaje_actual(self):
        texto = self.mensajes[self.indice_mensaje]
        max_ancho = config.WIDTH - 120
        self.escritor = TypewriterText(
            self.font, texto, (60, config.HEIGHT // 2 - 40), speed=0.04, max_width=max_ancho
        )

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
        self.tiempo += dt
        self.particulas.update(dt)
        if self.escritor:
            self.escritor.actualizar(dt)

    def dibujar(self, superficie):
        superficie.blit(self.bg_surf, (0, 0))
        self.particulas.draw(superficie)

        ProceduralUI.draw_panel(
            superficie, self.panel_rect,
            bg_color=(14, 12, 22, 215),
            border_color=config.COLOR_ENERGY,
            cut=14,
            glow=True
        )

        # Indicadores de página de transmisión
        total = len(self.mensajes)
        for i in range(total):
            nx = self.panel_rect.left + 28 + i * 18
            ny = self.panel_rect.bottom - 18
            activo = (i == self.indice_mensaje)
            col = config.COLOR_ENERGY if activo else (80, 80, 95)
            pygame.draw.circle(superficie, col, (nx, ny), 4 if activo else 3)

        if self.escritor:
            self.escritor.dibujar(superficie)
            if self.escritor.finished:
                pulso = 0.55 + 0.45 * math.sin(self.tiempo * 5.5)
                c_hint = (int(200 * pulso), int(200 * pulso), int(220 * pulso))
                hint = self.fuente_hint.render("[ ESPACIO / CLIC PARA CONTINUAR ]", True, c_hint)
                superficie.blit(hint, (self.panel_rect.right - hint.get_width() - 24, self.panel_rect.bottom - 26))
