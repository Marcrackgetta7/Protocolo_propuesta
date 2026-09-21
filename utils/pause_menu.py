import pygame
import config
from entities.ui_button import UIButton

class PauseMenu:
    def __init__(self, maquina):
        self.maquina = maquina
        self.fuente_titulo = pygame.font.SysFont("consolas", 40, bold=True)
        
        cx = config.WIDTH // 2 - 100
        cy = config.HEIGHT // 2 - 50
        
        self.btn_continuar = UIButton(cx, cy, 200, 40, "Continuar")
        self.btn_reintentar = UIButton(cx, cy + 60, 200, 40, "Reintentar")
        self.btn_salir = UIButton(cx, cy + 120, 200, 40, "Salir")

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
            self.maquina.state.startup()
        elif self.btn_salir.clic(pos_raton, clic_izq):
            self.maquina.pausado = False
            self.maquina.state.next_state = "MAIN_MENU"
            self.maquina.state.done = True

    def actualizar(self, dt):
        pos_raton = pygame.mouse.get_pos()
        self.btn_continuar.actualizar(pos_raton)
        self.btn_reintentar.actualizar(pos_raton)
        self.btn_salir.actualizar(pos_raton)

    def dibujar(self, superficie):
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        superficie.blit(overlay, (0, 0))

        tit = self.fuente_titulo.render("PAUSA", True, config.COLOR_TEXT)
        superficie.blit(tit, tit.get_rect(center=(config.WIDTH//2, config.HEIGHT//2 - 120)))

        pos_raton = pygame.mouse.get_pos()
        self.btn_continuar.dibujar(superficie, pos_raton)
        self.btn_reintentar.dibujar(superficie, pos_raton)
        self.btn_salir.dibujar(superficie, pos_raton)