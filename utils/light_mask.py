import pygame
import config
from utils.vfx import _CACHE


class LightMask:
    """Crea la niebla de guerra para el laberinto de la Fase 2 con gradiente pre-calculado."""
    def __init__(self):
        self.superficie = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        self.radio_luz = 130  # Qué tan grande es el círculo de visión
        self.estampa_luz = self._get_light_stamp(self.radio_luz)

    @staticmethod
    def _get_light_stamp(radio_luz):
        key = ("light_mask_stamp", radio_luz)
        if key not in _CACHE:
            r_total = radio_luz + 35
            size = r_total * 2
            stamp = pygame.Surface((size, size), pygame.SRCALPHA)
            stamp.fill((0, 0, 0, 255))
            # Degradado suave desde el borde exterior hasta el centro transparente
            steps = 28
            for i in range(steps, 0, -1):
                t = i / steps
                rad = int(radio_luz * 0.65 + (r_total - radio_luz * 0.65) * t)
                alpha = int(255 * (t ** 2))
                pygame.draw.circle(stamp, (0, 0, 0, alpha), (r_total, r_total), rad)
            pygame.draw.circle(stamp, (0, 0, 0, 0), (r_total, r_total), int(radio_luz * 0.65))
            _CACHE[key] = stamp
        return _CACHE[key]

    def dibujar(self, pantalla, pos_jugador):
        # 1. Llenar toda la superficie de negro completamente opaco
        self.superficie.fill((0, 0, 0, 255))

        # 2. Estampar el gradiente pre-calculado con BLEND_RGBA_MIN en O(1)
        r_total = self.estampa_luz.get_width() // 2
        px = int(pos_jugador[0]) - r_total
        py = int(pos_jugador[1]) - r_total
        self.superficie.blit(self.estampa_luz, (px, py), special_flags=pygame.BLEND_RGBA_MIN)

        # 3. Dibujar la máscara completa sobre el juego
        pantalla.blit(self.superficie, (0, 0))
