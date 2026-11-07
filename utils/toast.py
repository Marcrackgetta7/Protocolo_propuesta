import pygame
from utils.fonts import get_font
from utils.vfx import GlowCache, ProceduralUI
import config
from utils import audio


class ToastManager:
    _instancia = None

    @classmethod
    def get(cls):
        if cls._instancia is None:
            cls._instancia = ToastManager()
        return cls._instancia

    def __init__(self):
        self.toasts = []  # Lista de diccionarios con info del toast
        self.fuente_tit = None
        self.fuente_txt = None

    def mostrar(self, titulo, mensaje, duracion=4.0):
        if not pygame.font.get_init():
            return

        if self.fuente_tit is None:
            self.fuente_tit = get_font(20, bold=True)
            self.fuente_txt = get_font(16)

        self.toasts.append({
            "titulo": titulo,
            "mensaje": mensaje,
            "tiempo_restante": duracion,
            "tiempo_total": duracion,
            "y_offset": -100  # Empezar arriba de la pantalla (animación)
        })
        audio.reproducir("anomalia")

    def actualizar(self, dt):
        for t in self.toasts[:]:
            t["tiempo_restante"] -= dt

            # Animación de entrada
            if t["tiempo_restante"] > t["tiempo_total"] - 0.5:
                t["y_offset"] += (20 - t["y_offset"]) * 10 * dt
            # Animación de salida
            elif t["tiempo_restante"] < 0.5:
                t["y_offset"] += (-100 - t["y_offset"]) * 10 * dt

            if t["tiempo_restante"] <= 0:
                self.toasts.remove(t)

    def dibujar(self, superficie):
        for i, t in enumerate(self.toasts):
            rect_w, rect_h = 420, 74
            rect_x = config.WIDTH // 2 - rect_w // 2
            rect_y = int(t["y_offset"]) + (i * (rect_h + 10))
            rect_toast = pygame.Rect(rect_x, rect_y, rect_w, rect_h)

            ProceduralUI.draw_panel(
                superficie, rect_toast,
                bg_color=(16, 12, 24, 235),
                border_color=config.COLOR_ENERGY,
                cut=10,
                glow=True
            )

            # Ícono de trofeo/insignia energética a la izquierda
            ix, iy = rect_x + 26, rect_y + 34
            GlowCache.blit(superficie, ix, iy, 22, config.COLOR_ENERGY, intensity=0.55)
            pts_rombo = [(ix, iy - 12), (ix + 12, iy), (ix, iy + 12), (ix - 12, iy)]
            pygame.draw.polygon(superficie, config.COLOR_ENERGY, pts_rombo)
            pygame.draw.polygon(superficie, (255, 255, 255), pts_rombo, 2)

            # Textos
            tit_surf = self.fuente_tit.render(t["titulo"], True, config.COLOR_ENERGY)
            msg_surf = self.fuente_txt.render(t["mensaje"], True, (255, 255, 255))

            superficie.blit(tit_surf, (rect_x + 50, rect_y + 10))
            superficie.blit(msg_surf, (rect_x + 50, rect_y + 36))

            # Barra de tiempo restante en la base
            progreso = max(0.0, min(1.0, t["tiempo_restante"] / max(0.01, t["tiempo_total"])))
            bar_w = int((rect_w - 28) * progreso)
            if bar_w > 0:
                pygame.draw.rect(
                    superficie, config.COLOR_ENERGY,
                    (rect_x + 14, rect_y + rect_h - 6, bar_w, 3)
                )
