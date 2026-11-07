import math
import pygame
from utils.fonts import get_font
from states.base_state import BaseState
from utils import save_manager
from utils.vfx import GlowCache, GradientCache, FloatingParticles, ProceduralUI
import config


class MainMenu(BaseState):
    def __init__(self):
        super().__init__()
        self.datos = save_manager.cargar()
        self.fuente_titulo = get_font(40, bold=True)
        self.fuente_botones = get_font(20)
        self.TOTAL_LOGROS = 9
        self.TOTAL_FASES = 8
        self.tiempo = 0.0

        # Fondos y sistemas de partículas pre-calculados para los 3 arcos del juego
        self.bg_xmas = GradientCache.get_vertical(
            config.WIDTH, config.HEIGHT, (10, 26, 38), (18, 42, 28), vignette=True
        )
        self.bg_cyber = GradientCache.get_vertical(
            config.WIDTH, config.HEIGHT, (16, 4, 8), (6, 6, 10), vignette=True
        )
        self.bg_complete = GradientCache.get_vertical(
            config.WIDTH, config.HEIGHT, (14, 6, 22), (28, 8, 24), vignette=True
        )

        self.particulas_xmas = FloatingParticles(count=45, mode="snow")
        self.particulas_cyber = FloatingParticles(count=40, mode="cyber")
        self.particulas_complete = FloatingParticles(count=45, mode="romantic")

        self.actualizar_botones()

    def startup(self):
        self.done = False
        self.next_state = None
        self.datos = save_manager.cargar()
        self.actualizar_botones()

    def actualizar_botones(self):
        fase = self.datos.get("fase_desbloqueada", 1)
        secretos = self.datos.get("secretos", [])
        self.botones = {}

        cx = config.WIDTH // 2

        if fase < 5:
            self.botones["Regalo 1: Nieve"] = {"rect": pygame.Rect(cx - 390, 195, 370, 48), "fase": 1, "destino": "INTRO_1"}
            self.botones["Regalo 2: Bosque"] = {"rect": pygame.Rect(cx - 390, 265, 370, 48), "fase": 2, "destino": "INTRO_2"}
            self.botones["Regalo 3: Entregas"] = {"rect": pygame.Rect(cx + 20, 195, 370, 48), "fase": 3, "destino": "INTRO_3"}
            self.botones["Regalo 4: El Jefe"] = {"rect": pygame.Rect(cx + 20, 265, 370, 48), "fase": 4, "destino": "INTRO_4"}
        elif fase < 8:
            self.botones["Brecha 1: Infiltración"] = {"rect": pygame.Rect(cx - 390, 195, 370, 48), "fase": 5, "destino": "INTRO"}
            self.botones["Brecha 2: Laberinto"] = {"rect": pygame.Rect(cx - 390, 265, 370, 48), "fase": 6, "destino": "INTRO_6"}
            self.botones["Brecha 3: El Núcleo"] = {"rect": pygame.Rect(cx + 20, 195, 370, 48), "fase": 7, "destino": "INTRO_7"}
            self.botones["Registro de Logros"] = {"rect": pygame.Rect(cx + 20, 265, 370, 48), "fase": 1, "destino": "ACHIEVEMENTS"}
        else:
            self.botones["Regalo 1: Nieve"] = {"rect": pygame.Rect(cx - 410, 165, 390, 42), "fase": 1, "destino": "INTRO_1"}
            self.botones["Regalo 2: Bosque"] = {"rect": pygame.Rect(cx - 410, 217, 390, 42), "fase": 2, "destino": "INTRO_2"}
            self.botones["Regalo 3: Entregas"] = {"rect": pygame.Rect(cx - 410, 269, 390, 42), "fase": 3, "destino": "INTRO_3"}
            self.botones["Regalo 4: El Jefe"] = {"rect": pygame.Rect(cx - 410, 321, 390, 42), "fase": 4, "destino": "INTRO_4"}
            self.botones["Brecha 1: Infiltración"] = {"rect": pygame.Rect(cx + 20, 165, 390, 42), "fase": 5, "destino": "INTRO"}
            self.botones["Brecha 2: Laberinto"] = {"rect": pygame.Rect(cx + 20, 217, 390, 42), "fase": 6, "destino": "INTRO_6"}
            self.botones["Brecha 3: El Núcleo"] = {"rect": pygame.Rect(cx + 20, 269, 390, 42), "fase": 7, "destino": "INTRO_7"}
            self.botones["Registro de Logros"] = {"rect": pygame.Rect(cx + 20, 321, 390, 42), "fase": 1, "destino": "ACHIEVEMENTS"}

            if len(secretos) >= self.TOTAL_LOGROS:
                self.botones["ARCHIVOS OCULTOS"] = {"rect": pygame.Rect(cx - 220, 385, 440, 44), "fase": 8, "destino": "GALLERY"}
            else:
                self.botones[f"FALTAN {self.TOTAL_LOGROS - len(secretos)} LOGROS"] = {"rect": pygame.Rect(cx - 220, 385, 440, 44), "fase": 99, "destino": "NONE"}

        # Botones inferiores con márgenes limpios
        self.botones["Configuración"] = {"rect": pygame.Rect(40, config.HEIGHT - 55, 200, 40), "fase": 1, "destino": "SETTINGS"}
        self.botones["Estadísticas"] = {"rect": pygame.Rect(config.WIDTH - 240, config.HEIGHT - 55, 200, 40), "fase": 1, "destino": "STATS"}

    def manejar_eventos(self, evento):
        if self.done:
            return
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos_raton = pygame.mouse.get_pos()
            for nombre, info in self.botones.items():
                if info["rect"].collidepoint(pos_raton):
                    if info["destino"] != "NONE" and self.datos.get("fase_desbloqueada", 1) >= info["fase"]:
                        self.next_state = info["destino"]
                        self.done = True
                    else:
                        from utils import audio
                        audio.reproducir("explosion")  # Feedback de botón bloqueado
                    break

    def actualizar(self, dt):
        self.tiempo += dt
        fase_actual = self.datos.get("fase_desbloqueada", 1)
        if fase_actual < 5:
            self.particulas_xmas.update(dt)
        elif fase_actual < 8:
            self.particulas_cyber.update(dt)
        else:
            self.particulas_complete.update(dt)

    def dibujar(self, superficie):
        fase_actual = self.datos.get("fase_desbloqueada", 1)
        secretos = self.datos.get("secretos", [])

        if fase_actual < 5:
            superficie.blit(self.bg_xmas, (0, 0))
            self.particulas_xmas.draw(superficie)
            color_tema = (255, 110, 110)
            titulo_texto = "UN CUENTO DE NAVIDAD"
        elif fase_actual < 8:
            superficie.blit(self.bg_cyber, (0, 0))
            # Líneas de matriz roja sutiles
            offset_grid = int(self.tiempo * 25) % 40
            for x in range(0, config.WIDTH, 80):
                pygame.draw.line(superficie, (28, 8, 12), (x, 0), (x, config.HEIGHT), 1)
            for y in range(offset_grid, config.HEIGHT, 40):
                pygame.draw.line(superficie, (28, 8, 12), (0, y), (config.WIDTH, y), 1)
            self.particulas_cyber.draw(superficie)
            color_tema = config.COLOR_DANGER
            titulo_texto = "SISTEMA COMPROMETIDO"
        else:
            superficie.blit(self.bg_complete, (0, 0))
            self.particulas_complete.draw(superficie)
            color_tema = config.COLOR_ENERGY
            titulo_texto = "PROTOCOLO: COMPLETADO"

        # Título con halo reactivo
        GlowCache.blit(superficie, config.WIDTH // 2, 55, 140, color_tema, intensity=0.35)
        titulo_surf = self.fuente_titulo.render(titulo_texto, True, color_tema)
        superficie.blit(titulo_surf, titulo_surf.get_rect(center=(config.WIDTH // 2, 55)))

        pasos_completados = min(fase_actual - 1, 7) + len(secretos)
        progreso = min(1.0, pasos_completados / 16.0)

        # Barra de progreso estilizada
        bar_rect = pygame.Rect(config.WIDTH // 2 - 320, 95, 640, 16)
        pygame.draw.rect(superficie, (25, 25, 32), bar_rect)
        ancho_prog = int(640 * progreso)
        if ancho_prog > 0:
            pygame.draw.rect(superficie, color_tema, (bar_rect.x, bar_rect.y, ancho_prog, 16))
            GlowCache.blit(superficie, bar_rect.x + ancho_prog, bar_rect.centery, 18, color_tema, intensity=0.55)
        pygame.draw.rect(superficie, (180, 180, 195), bar_rect, 1)

        txt_progreso = self.fuente_botones.render(
            f"Progreso Total del Sistema: {int(progreso * 100)}%", True, (255, 255, 255)
        )
        superficie.blit(txt_progreso, txt_progreso.get_rect(center=(config.WIDTH // 2, 125)))

        pos_raton = pygame.mouse.get_pos()
        for nombre, info in self.botones.items():
            rect = info["rect"]
            desbloqueado = fase_actual >= info["fase"]
            hover = desbloqueado and rect.collidepoint(pos_raton)

            if not desbloqueado:
                bg_col = (20, 20, 24, 190)
                borde_col = (75, 75, 85)
                color_texto = (100, 100, 110)
            elif hover:
                bg_col = (65, 25, 45, 235)
                borde_col = color_tema
                color_texto = (255, 255, 255)
            else:
                bg_col = (32, 30, 42, 210)
                borde_col = (150, 150, 165)
                color_texto = config.COLOR_TEXT

            if "ARCHIVOS OCULTOS" in nombre:
                pulso = 0.65 + 0.35 * math.sin(self.tiempo * 5.0)
                bg_col = (80, 12, 45, 235)
                borde_col = config.COLOR_ENERGY
                GlowCache.blit(superficie, rect.centerx, rect.centery, 85, config.COLOR_ENERGY, intensity=0.5 * pulso)
            elif "Registro de" in nombre:
                bg_col = (60, 52, 18, 220) if not hover else (90, 78, 25, 235)
                borde_col = (255, 215, 0)

            ProceduralUI.draw_panel(
                superficie, rect,
                bg_color=bg_col,
                border_color=borde_col,
                cut=8,
                glow=hover
            )

            texto_surf = self.fuente_botones.render(nombre, True, color_texto)
            superficie.blit(texto_surf, texto_surf.get_rect(center=rect.center))
