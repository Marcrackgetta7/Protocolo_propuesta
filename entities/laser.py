import math
import pygame
import config
from utils.vfx import _CACHE


class Laser:
    def __init__(self, es_horizontal, pos):
        self.es_horizontal = es_horizontal
        self.pos = pos
        self.timer = 0.0
        # Velocidad de aviso balanceada para permitir reacción adecuada
        self.tiempo_aviso = 0.85
        self.tiempo_activo = 0.35
        self.terminado = False
        self.estado = "AVISO"
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.grosor = 30

    @staticmethod
    def _get_beam_glow(es_horizontal, grosor):
        key = ("laser_beam_glow", es_horizontal, grosor)
        if key not in _CACHE:
            pad = 18
            total = grosor + pad * 2
            if es_horizontal:
                surf = pygame.Surface((config.WIDTH, total))
                cy = total // 2
                for offset in range(cy, 0, -1):
                    ratio = (1.0 - (offset / cy)) ** 1.8
                    col = (int(config.COLOR_DANGER[0] * ratio * 0.65), 0, int(25 * ratio))
                    pygame.draw.line(surf, col, (0, cy - offset), (config.WIDTH, cy - offset))
                    pygame.draw.line(surf, col, (0, cy + offset), (config.WIDTH, cy + offset))
            else:
                surf = pygame.Surface((total, config.HEIGHT))
                cx = total // 2
                for offset in range(cx, 0, -1):
                    ratio = (1.0 - (offset / cx)) ** 1.8
                    col = (int(config.COLOR_DANGER[0] * ratio * 0.65), 0, int(25 * ratio))
                    pygame.draw.line(surf, col, (cx - offset, 0), (cx - offset, config.HEIGHT))
                    pygame.draw.line(surf, col, (cx + offset, 0), (cx + offset, config.HEIGHT))
            _CACHE[key] = surf
        return _CACHE[key]

    def actualizar(self, dt):
        self.timer += dt
        if self.estado == "AVISO":
            if self.timer >= self.tiempo_aviso:
                self.estado = "ACTIVO"
                self.timer = 0.0
        elif self.estado == "ACTIVO":
            if self.timer >= self.tiempo_activo:
                self.terminado = True

    def dibujar(self, superficie):
        if self.es_horizontal:
            self.rect = pygame.Rect(0, self.pos - self.grosor // 2, config.WIDTH, self.grosor)
        else:
            self.rect = pygame.Rect(self.pos - self.grosor // 2, 0, self.grosor, config.HEIGHT)

        if self.estado == "AVISO":
            progreso = min(1.0, self.timer / max(0.01, self.tiempo_aviso))
            pulso = 0.5 + 0.5 * math.sin(self.timer * (14.0 + progreso * 28.0))
            c_borde = (int(180 + 75 * pulso), int(160 * (1.0 - progreso * 0.6)), int(160 * (1.0 - progreso * 0.6)))
            pygame.draw.rect(superficie, c_borde, self.rect, 2)

            # Línea guía central de puntería
            if self.es_horizontal:
                pygame.draw.line(superficie, (255, 80, 80), (0, int(self.pos)), (config.WIDTH, int(self.pos)), 1)
            else:
                pygame.draw.line(superficie, (255, 80, 80), (int(self.pos), 0), (int(self.pos), config.HEIGHT), 1)

        elif self.estado == "ACTIVO":
            glow_surf = self._get_beam_glow(self.es_horizontal, self.grosor)
            if self.es_horizontal:
                superficie.blit(glow_surf, (0, self.rect.y - 18), special_flags=pygame.BLEND_RGB_ADD)
                pygame.draw.rect(superficie, config.COLOR_DANGER, self.rect)
                nucleo_h = max(6, int(self.grosor * 0.35))
                pygame.draw.rect(
                    superficie, (255, 240, 240),
                    (0, int(self.pos) - nucleo_h // 2, config.WIDTH, nucleo_h)
                )
            else:
                superficie.blit(glow_surf, (self.rect.x - 18, 0), special_flags=pygame.BLEND_RGB_ADD)
                pygame.draw.rect(superficie, config.COLOR_DANGER, self.rect)
                nucleo_w = max(6, int(self.grosor * 0.35))
                pygame.draw.rect(
                    superficie, (255, 240, 240),
                    (int(self.pos) - nucleo_w // 2, 0, nucleo_w, config.HEIGHT)
                )
