import math
import random
import pygame
from utils.fonts import get_font
from utils.vfx import GlowCache, ProceduralUI
import config


class UIButton:
    def __init__(self, x, y, ancho, alto, texto, evasivo=False):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.evasivo = evasivo
        self.fuente = get_font(24)
        self.color_normal = (40, 40, 40)
        self.color_hover = config.COLOR_ENERGY  # Se ilumina en rosa al pasar el ratón
        self.intentos_evasion = 0
        self.visible = True

    def actualizar(self, pos_raton):
        if not self.visible:
            return

        # Lógica de evasión (IA de proximidad mediante distancia euclidiana)
        if self.evasivo:
            centro_x = self.rect.x + self.rect.width / 2
            centro_y = self.rect.y + self.rect.height / 2
            distancia = math.hypot(pos_raton[0] - centro_x, pos_raton[1] - centro_y)

            # Si el ratón se acerca a menos de 100 píxeles...
            if distancia < 100:
                self.intentos_evasion += 1

                # A los 5 intentos, el botón desaparece según el GDD
                if self.intentos_evasion > 5:
                    self.visible = False
                else:
                    if self.intentos_evasion == 3:
                        self.texto = "¿Segura?"
                    elif self.intentos_evasion == 4:
                        self.texto = "Casi..."

                    # Teletransportar a una posición aleatoria dentro de la pantalla
                    self.rect.x = random.randint(50, config.WIDTH - self.rect.width - 50)
                    self.rect.y = random.randint(50, config.HEIGHT - self.rect.height - 50)

    def dibujar(self, superficie, pos_raton):
        if not self.visible:
            return

        hover = self.rect.collidepoint(pos_raton)
        borde_col = self.color_hover if hover else config.COLOR_TEXT
        bg_col = (
            min(255, self.color_hover[0] // 3 + 15),
            min(255, self.color_hover[1] // 3 + 10),
            min(255, self.color_hover[2] // 3 + 20),
            230
        ) if hover else (
            self.color_normal[0],
            self.color_normal[1],
            self.color_normal[2],
            210
        )

        if hover:
            GlowCache.blit(
                superficie, self.rect.centerx, self.rect.centery,
                max(self.rect.width, self.rect.height) // 2, self.color_hover, intensity=0.38
            )

        ProceduralUI.draw_panel(
            superficie, self.rect,
            bg_color=bg_col,
            border_color=borde_col,
            cut=8,
            glow=False
        )

        # Indicadores laterales en hover
        if hover:
            pygame.draw.line(
                superficie, self.color_hover,
                (self.rect.left + 6, self.rect.top + 10),
                (self.rect.left + 6, self.rect.bottom - 10), 3
            )
            pygame.draw.line(
                superficie, self.color_hover,
                (self.rect.right - 7, self.rect.top + 10),
                (self.rect.right - 7, self.rect.bottom - 10), 3
            )

        texto_surf = self.fuente.render(self.texto, True, config.COLOR_TEXT)
        texto_rect = texto_surf.get_rect(center=self.rect.center)
        superficie.blit(texto_surf, texto_rect)

    def clic(self, pos_raton, clic_izq):
        if self.visible and clic_izq and self.rect.collidepoint(pos_raton):
            return True
        return False
