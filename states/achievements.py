import pygame
from utils.fonts import get_font
from states.base_state import BaseState
from utils import save_manager
from utils.vfx import GlowCache, GradientCache, ProceduralUI
import config

LOGROS_DATA = [
    {"id": "L1", "tipo": "LOGRO", "nombre": "Manos Ágiles", "desc": "Fase 1: Atrapa los regalos. (Margen de error: Máximo 1 caída)."},
    {"id": "L2", "tipo": "LOGRO", "nombre": "Velocista Nevado", "desc": "Fase 2: Escapa del laberinto en menos de 15 segundos."},
    {"id": "L3", "tipo": "LOGRO", "nombre": "Santa Veloz", "desc": "Fase 3: Entrega todos los regalos y que te sobren 5+ segundos."},
    {"id": "L4", "tipo": "LOGRO", "nombre": "Sangre Caliente", "desc": "Fase 4: Vence al Muñeco de Nieve sin que tu barra de frío llegue a 100%."},
    {"id": "L5", "tipo": "LOGRO", "nombre": "Fantasma Digital", "desc": "Fase 5: Completa la infiltración sin que ningún láser te toque."},
    {"id": "L6", "tipo": "LOGRO", "nombre": "Fuerza Bruta", "desc": "Fase 6: Destruye al menos 3 cortafuegos del mapa antes de escapar."},
    {"id": "Pacifista", "tipo": "LOGRO", "nombre": "Pacifista", "desc": "Fase 7: Sobrevive 15 segundos de combate contra el Núcleo sin disparar."},
    {"id": "Estrella Helada", "tipo": "SECRETO", "nombre": "Estrella Helada", "desc": "Acertijo: En el bosque, busca la pared que no es pared antes de la luz final."},
    {"id": "Código Muerto", "tipo": "SECRETO", "nombre": "Código Muerto", "desc": "Acertijo: En el abismo del laberinto, la esquina inferior izquierda oculta un fantasma."}
]


class Achievements(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "MAIN_MENU"
        self.fuente_titulo = get_font(30, bold=True)
        self.fuente_nombre = get_font(18, bold=True)
        self.fuente_desc = get_font(14)
        self.datos = save_manager.cargar()
        self.scroll_y = 0
        self.bg_surf = GradientCache.get_vertical(
            config.WIDTH, config.HEIGHT, (10, 8, 18), (6, 6, 12), vignette=True
        )

    def startup(self):
        self.datos = save_manager.cargar()
        self.scroll_y = 0

    def manejar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self.done = True
        if evento.type == pygame.MOUSEWHEEL:
            self.scroll_y += evento.y * 30

    def actualizar(self, dt):
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_UP]:
            self.scroll_y += 300 * dt
        if teclas[pygame.K_DOWN]:
            self.scroll_y -= 300 * dt

        if self.scroll_y > 0:
            self.scroll_y = 0
        min_scroll = -max(0, (len(LOGROS_DATA) * 65) - (config.HEIGHT - 135))
        if self.scroll_y < min_scroll:
            self.scroll_y = min_scroll

    def dibujar(self, superficie):
        superficie.blit(self.bg_surf, (0, 0))

        y_base = int(120 + self.scroll_y)
        secretos_obtenidos = self.datos.get("secretos", [])

        for item in LOGROS_DATA:
            if y_base > -70 and y_base < config.HEIGHT + 20:
                desbloqueado = item["id"] in secretos_obtenidos
                rect_item = pygame.Rect(config.WIDTH // 2 - 440, y_base, 880, 55)

                if desbloqueado:
                    color_fondo = (16, 48, 24, 220) if item["tipo"] == "LOGRO" else (55, 45, 16, 220)
                    color_borde = (50, 220, 80) if item["tipo"] == "LOGRO" else (255, 215, 0)
                    estado_txt = "[ DESBLOQUEADO ]"
                else:
                    color_fondo = (20, 20, 26, 200)
                    color_borde = (80, 80, 95)
                    estado_txt = "[ BLOQUEADO ]"

                ProceduralUI.draw_panel(
                    superficie, rect_item,
                    bg_color=color_fondo,
                    border_color=color_borde,
                    cut=8,
                    glow=desbloqueado
                )

                # Medalla / nodo lateral
                ix, iy = rect_item.x + 22, rect_item.centery
                if desbloqueado:
                    GlowCache.blit(superficie, ix, iy, 18, color_borde, intensity=0.5)
                    pygame.draw.circle(superficie, color_borde, (ix, iy), 7)
                else:
                    pygame.draw.circle(superficie, color_borde, (ix, iy), 6, 2)

                txt_nombre = self.fuente_nombre.render(f"{item['tipo']} - {item['nombre']}", True, color_borde)
                txt_desc = self.fuente_desc.render(item["desc"], True, (210, 210, 220))
                txt_estado = self.fuente_nombre.render(estado_txt, True, color_borde)

                superficie.blit(txt_nombre, (rect_item.x + 42, rect_item.y + 8))
                superficie.blit(txt_desc, (rect_item.x + 42, rect_item.y + 30))
                superficie.blit(txt_estado, (rect_item.right - 180, rect_item.y + 18))

            y_base += 65

        # Cabecera fija
        pygame.draw.rect(superficie, (8, 8, 14), (0, 0, config.WIDTH, 102))
        GlowCache.blit(superficie, config.WIDTH // 2, 40, 120, config.COLOR_ENERGY, intensity=0.3)
        tit = self.fuente_titulo.render("BASE DE DATOS: LOGROS Y SECRETOS", True, config.COLOR_ENERGY)
        superficie.blit(tit, tit.get_rect(center=(config.WIDTH // 2, 40)))

        inst = self.fuente_desc.render(
            f"Progreso Total: {len(secretos_obtenidos)}/9  |  [ Usa las flechas/rueda para bajar | ESC para volver ]",
            True, (165, 165, 180)
        )
        superficie.blit(inst, inst.get_rect(center=(config.WIDTH // 2, 75)))
        pygame.draw.line(superficie, config.COLOR_ENERGY, (50, 100), (config.WIDTH - 50, 100), 2)
