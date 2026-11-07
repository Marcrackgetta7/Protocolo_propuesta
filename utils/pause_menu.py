import pygame
from utils.fonts import get_font
from utils.vfx import GlowCache, ProceduralUI
import config
from entities.ui_button import UIButton


class PauseMenu:
    def __init__(self, maquina):
        self.maquina = maquina
        self.fuente_titulo = get_font(40, bold=True)

        cx = config.WIDTH // 2 - 120
        cy = config.HEIGHT // 2 - 55

        self.btn_continuar = UIButton(cx, cy, 240, 44, "Continuar")
        self.btn_reintentar = UIButton(cx, cy + 58, 240, 44, "Reintentar")
        self.btn_salir = UIButton(cx, cy + 116, 240, 44, "Salir")

        # Superficie de oscurecimiento pre-calculada una sola vez
        self.overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((5, 5, 10, 205))
        self.panel_rect = pygame.Rect(config.WIDTH // 2 - 180, config.HEIGHT // 2 - 165, 360, 310)

    def manejar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self.maquina.pausado = False
            return

        clic_izq = (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1)
        pos_raton = pygame.mouse.get_pos()

        if self.btn_continuar.clic(pos_raton, clic_izq):
            self.maquina.pausado = False
        elif self.btn_reintentar.clic(pos_raton, clic_izq):
            self.maquina.pausado = False
            self.maquina.state.time_active = 0.0
            if hasattr(self.maquina.state, "cleanup"):
                self.maquina.state.cleanup()
            self.maquina.state.done = False
            self.maquina.state.startup()
        elif self.btn_salir.clic(pos_raton, clic_izq):
            self.maquina.pausado = False
            self.maquina.mostrando_controles = False
            self.maquina.state.time_active = 0.0
            self.maquina.estado_siguiente_nombre = "MAIN_MENU"
            self.maquina.haciendo_fade_out = True
            self.maquina.alpha_fade = 0.0
            self.maquina.state.done = False

    def actualizar(self, dt):
        pos_raton = pygame.mouse.get_pos()
        self.btn_continuar.actualizar(pos_raton)
        self.btn_reintentar.actualizar(pos_raton)
        self.btn_salir.actualizar(pos_raton)

    def dibujar(self, superficie):
        superficie.blit(self.overlay, (0, 0))

        ProceduralUI.draw_panel(
            superficie, self.panel_rect,
            bg_color=(14, 12, 22, 235),
            border_color=config.COLOR_ENERGY,
            cut=14,
            glow=True
        )

        GlowCache.blit(superficie, config.WIDTH // 2, config.HEIGHT // 2 - 120, 75, config.COLOR_ENERGY, intensity=0.35)
        tit = self.fuente_titulo.render("PAUSA", True, config.COLOR_TEXT)
        superficie.blit(tit, tit.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2 - 120)))

        pos_raton = pygame.mouse.get_pos()
        self.btn_continuar.dibujar(superficie, pos_raton)
        self.btn_reintentar.dibujar(superficie, pos_raton)
        self.btn_salir.dibujar(superficie, pos_raton)
