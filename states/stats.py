import pygame
from utils.fonts import get_font
from states.base_state import BaseState
from utils import save_manager
from utils.vfx import GlowCache, GradientCache, ProceduralUI
import config


class Stats(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "MAIN_MENU"
        self.fuente_titulo = get_font(30, bold=True)
        self.fuente_normal = get_font(20)
        self.fuente_fases = get_font(18)
        self.datos = save_manager.cargar()
        self.scroll_y = 0
        self.bg_surf = GradientCache.get_vertical(
            config.WIDTH, config.HEIGHT, (8, 12, 20), (6, 6, 12), vignette=True
        )

    def startup(self):
        self.datos = save_manager.cargar()
        self.scroll_y = 0

    def manejar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self.done = True
        if evento.type == pygame.MOUSEWHEEL:
            self.scroll_y += evento.y * 30

    def formatear_tiempo(self, segundos):
        s = int(segundos)
        m = s // 60
        s = s % 60
        return f"{m:02d}:{s:02d}"

    def actualizar(self, dt):
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_UP]:
            self.scroll_y += 300 * dt
        if teclas[pygame.K_DOWN]:
            self.scroll_y -= 300 * dt

        if self.scroll_y > 0:
            self.scroll_y = 0

    def dibujar(self, superficie):
        superficie.blit(self.bg_surf, (0, 0))

        y_base = int(120 + self.scroll_y)

        times = self.datos.get("times", {})
        total_time = times.get("total", 0.0)
        time_100 = times.get("100_percent", 0.0)
        phases = times.get("phases", {})
        secretos_obtenidos = self.datos.get("secretos", [])

        # Bloque de Estadísticas Globales
        rect_global = pygame.Rect(config.WIDTH // 2 - 440, y_base, 880, 100)
        ProceduralUI.draw_panel(
            superficie, rect_global,
            bg_color=(16, 24, 36, 220),
            border_color=config.COLOR_ENERGY,
            cut=12,
            glow=True
        )

        txt_total = self.fuente_normal.render(
            f"Tiempo Total de Juego: {self.formatear_tiempo(total_time)}", True, (255, 255, 255)
        )
        superficie.blit(txt_total, (rect_global.x + 24, rect_global.y + 20))

        if time_100 > 0.0:
            txt_100 = self.fuente_normal.render(
                f"Tiempo para 100% Completado: {self.formatear_tiempo(time_100)}", True, (50, 255, 90)
            )
        else:
            txt_100 = self.fuente_normal.render(
                "Tiempo para 100% Completado: [No conseguido]", True, (130, 130, 145)
            )
        superficie.blit(txt_100, (rect_global.x + 24, rect_global.y + 58))

        y_base += 130

        # Bloque de Fases
        fases_ordenadas = [
            "XMAS_MINIGAME", "XMAS_MAZE", "XMAS_DELIVERY", "XMAS_BOSS",
            "MINIGAME", "HACK_MAZE", "HACK_BOSS"
        ]
        nombres_amigables = {
            "XMAS_MINIGAME": "Fase 1: Atrapando Regalos",
            "XMAS_MAZE": "Fase 2: Bosque Nevado",
            "XMAS_DELIVERY": "Fase 3: Entrega Nocturna",
            "XMAS_BOSS": "Fase 4: El Muñeco Gruñón",
            "MINIGAME": "Fase 5: Infiltración",
            "HACK_MAZE": "Fase 6: Laberinto de Cortafuegos",
            "HACK_BOSS": "Fase 7: El Núcleo"
        }

        for fase_clave in fases_ordenadas:
            if fase_clave in phases:
                rect_item = pygame.Rect(config.WIDTH // 2 - 440, y_base, 880, 42)
                ProceduralUI.draw_panel(
                    superficie, rect_item,
                    bg_color=(20, 20, 28, 205),
                    border_color=(95, 95, 115),
                    cut=6,
                    glow=False
                )

                nombre = nombres_amigables.get(fase_clave, fase_clave)
                tiempo = self.formatear_tiempo(phases[fase_clave])

                txt_nombre = self.fuente_fases.render(nombre, True, (215, 215, 225))
                txt_tiempo = self.fuente_fases.render(f"{tiempo}", True, config.COLOR_ENERGY)

                superficie.blit(txt_nombre, (rect_item.x + 18, rect_item.y + 10))
                superficie.blit(txt_tiempo, (rect_item.right - 95, rect_item.y + 10))

                y_base += 50

        # Límite de scroll
        min_scroll = -max(0, y_base - self.scroll_y - config.HEIGHT + 50)
        if self.scroll_y < min_scroll:
            self.scroll_y = min_scroll

        # Header fijo
        pygame.draw.rect(superficie, (8, 8, 14), (0, 0, config.WIDTH, 102))
        GlowCache.blit(superficie, config.WIDTH // 2, 40, 120, config.COLOR_ENERGY, intensity=0.3)
        tit = self.fuente_titulo.render("ESTADÍSTICAS DEL SISTEMA", True, config.COLOR_ENERGY)
        superficie.blit(tit, tit.get_rect(center=(config.WIDTH // 2, 40)))

        inst = self.fuente_fases.render(
            f"Secretos Descubiertos: {len(secretos_obtenidos)}/9  |  [ ESC para volver ]",
            True, (165, 165, 180)
        )
        superficie.blit(inst, inst.get_rect(center=(config.WIDTH // 2, 75)))
        pygame.draw.line(superficie, config.COLOR_ENERGY, (50, 100), (config.WIDTH - 50, 100), 2)
