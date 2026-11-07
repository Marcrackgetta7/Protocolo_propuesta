import math
import pygame
from states.base_state import BaseState
from utils.text_renderer import TypewriterText
from utils.vfx import GlowCache, GradientCache, FloatingParticles, ProceduralUI
import config


class Intro(BaseState):
    def __init__(self):
        super().__init__()
        # ¡AQUÍ ESTÁ EL CAMBIO! Ahora dirige al minijuego
        self.next_state = "MINIGAME"
        self.escritor = None
        self.tiempo = 0.0
        self.bg_surf = GradientCache.get_vertical(
            config.WIDTH, config.HEIGHT, (10, 4, 12), (4, 6, 12), vignette=True
        )
        self.particulas = FloatingParticles(count=30, mode="cyber")
        self.panel_rect = pygame.Rect(35, config.HEIGHT // 2 - 45, config.WIDTH - 70, 110)

    def startup(self):
        self.done = False
        self.next_state = "MINIGAME"
        self.tiempo = 0.0
        mensaje = "> INICIANDO PROTOCOLO: BRECHA... PRESIONA ESPACIO PARA SALTAR"
        self.escritor = TypewriterText(self.font, mensaje, (55, config.HEIGHT // 2 - 12), speed=0.05)

    def manejar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                self.done = True
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            self.done = True

    def actualizar(self, dt):
        self.tiempo += dt
        self.particulas.update(dt)
        if self.escritor:
            self.escritor.actualizar(dt)

    def dibujar(self, superficie):
        superficie.blit(self.bg_surf, (0, 0))
        self.particulas.draw(superficie)

        ProceduralUI.draw_panel(
            superficie, self.panel_rect,
            bg_color=(14, 10, 18, 215),
            border_color=config.COLOR_DANGER,
            cut=12,
            glow=True
        )

        if self.escritor:
            self.escritor.dibujar(superficie)
            if self.escritor.finished:
                pulso = 0.5 + 0.5 * math.sin(self.tiempo * 6.0)
                GlowCache.blit(
                    superficie, config.WIDTH - 80, self.panel_rect.bottom - 20,
                    18, config.COLOR_DANGER, intensity=0.6 * pulso
                )
