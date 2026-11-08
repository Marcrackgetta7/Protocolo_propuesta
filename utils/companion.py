import math
import pygame
from utils.fonts import get_font
from utils.text_renderer import TypewriterText
from utils.vfx import GlowCache, ProceduralUI
from utils import audio
import config


class CompanionUI:
    def __init__(self):
        self.fuente = get_font(18, bold=True)
        self.escritor = None
        self.y_fija = config.HEIGHT - 95  # Se queda siempre abajo
        self.tiempo = 0.0

        # Pre-calcular las dos versiones de panel (opaco y fantasma) para cero creación de Surface por frame
        self.panel_normal = ProceduralUI.get_panel(
            config.WIDTH - 40, 80, bg_color=(10, 14, 18, 220), border_color=(0, 255, 100, 255), cut=10
        )
        self.panel_fantasma = ProceduralUI.get_panel(
            config.WIDTH - 40, 80, bg_color=(10, 14, 18, 40), border_color=(0, 255, 100, 55), cut=10
        )
        self.retrato_normal = self._crear_base_retrato(255)
        self.retrato_fantasma = self._crear_base_retrato(55)

    @staticmethod
    def _crear_base_retrato(alpha):
        surf = pygame.Surface((60, 60), pygame.SRCALPHA)
        surf.fill((6, 22, 14, min(220, alpha)))
        for y in range(0, 60, 6):
            pygame.draw.line(surf, (0, 120, 55, min(90, alpha)), (0, y), (60, y), 1)
        pygame.draw.rect(surf, (0, 255, 100, alpha), (0, 0, 60, 60), 2)
        return surf

    def mostrar_mensaje(self, texto, id_voz=None):
        audio.detener_sonido("tecla")
        max_ancho = config.WIDTH - 140
        self.escritor = TypewriterText(
            self.fuente, texto, (105, self.y_fija + 16), speed=0.04, max_width=max_ancho
        )
        y_centrado = self.y_fija + max(10, (80 - self.escritor.total_height) // 2)
        self.escritor.pos = (105, y_centrado)
        if id_voz:
            audio.reproducir(id_voz, parar_anterior=True)

    def actualizar(self, dt):
        self.tiempo += dt
        if self.escritor:
            self.escritor.actualizar(dt)

    def dibujar(self, superficie, jugador_y=0):
        es_fantasma = jugador_y > config.HEIGHT - 150
        alfa_texto = 100 if es_fantasma else 255

        if self.escritor:
            y_centrado = self.y_fija + max(10, (80 - self.escritor.total_height) // 2)
            self.escritor.pos = (105, y_centrado)

        panel = self.panel_fantasma if es_fantasma else self.panel_normal
        retrato = self.retrato_fantasma if es_fantasma else self.retrato_normal

        if not es_fantasma:
            GlowCache.blit(superficie, 60, self.y_fija + 40, 48, (0, 255, 100), intensity=0.25)

        superficie.blit(panel, (20, self.y_fija))
        rx, ry = 30, self.y_fija + 10
        superficie.blit(retrato, (rx, ry))

        # Osciloscopio procedural sincronizado con escritor.finished == False
        hablando = self.escritor is not None and not self.escritor.finished
        color_onda = (0, 255, 120) if not es_fantasma else (0, 120, 60)
        cy = ry + 30
        pts = []
        for i in range(11):
            x = rx + 5 + i * 5
            if hablando:
                amp = math.sin(self.tiempo * 22.0 + i * 0.9) * math.cos(self.tiempo * 13.0 - i * 0.5) * 16.0
            else:
                amp = math.sin(self.tiempo * 3.0 + i * 0.6) * 2.5
            pts.append((x, int(cy + amp)))
        if len(pts) > 1:
            pygame.draw.lines(superficie, color_onda, False, pts, 2)

        if self.escritor:
            self.escritor.dibujar(superficie, alpha=alfa_texto)
