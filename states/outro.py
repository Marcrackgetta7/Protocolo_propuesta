import math
import pygame
from states.base_state import BaseState
from utils.vfx import (
    GlowCache,
    GradientCache,
    HeartRenderer,
    FloatingParticles,
    BurstPool,
    ProceduralUI,
)
import config


class Outro(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "OUTRO"
        self.tiempo = 0.0
        self.timer_burst = 0.0
        self.bg_surf = GradientCache.get_vertical(
            config.WIDTH, config.HEIGHT, (12, 4, 18), (34, 8, 26), vignette=True
        )
        self.particulas = FloatingParticles(count=55, mode="romantic")
        self.bursts = BurstPool(capacity=60)

    def startup(self):
        self.tiempo = 0.0
        self.timer_burst = 0.0
        self.bursts.emit(config.WIDTH // 2, config.HEIGHT // 2 - 40, count=28, heart_chance=0.65)

    def manejar_eventos(self, evento):
        # Permite cerrar el juego con Escape o la X de la ventana
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self.quit = True

    def actualizar(self, dt):
        self.tiempo += dt
        self.timer_burst += dt
        self.particulas.update(dt)
        self.bursts.update(dt)
        if self.timer_burst >= 1.8:
            self.timer_burst = 0.0
            self.bursts.emit(
                config.WIDTH // 2,
                config.HEIGHT // 2 - 55,
                count=14,
                heart_chance=0.55,
                speed_range=(35, 120)
            )

    def dibujar(self, superficie):
        superficie.blit(self.bg_surf, (0, 0))
        self.particulas.draw(superficie)

        cx, cy = config.WIDTH // 2, config.HEIGHT // 2
        pulso = 1.0 + 0.1 * math.sin(self.tiempo * 3.5)

        # Anillos de onda expansiva suaves
        onda_r = int(45 + ((self.tiempo * 45) % 140))
        pygame.draw.circle(superficie, (90, 20, 55), (cx, cy - 55), onda_r, 2)

        # Corazón central luminoso
        GlowCache.blit(superficie, cx, cy - 55, int(130 * pulso), config.COLOR_ENERGY, intensity=0.55)
        HeartRenderer.draw(
            superficie, cx, cy - 55,
            scale=1.9 * pulso,
            color=config.COLOR_ENERGY,
            alpha=235,
            glow=True
        )
        HeartRenderer.draw(
            superficie, cx, cy - 55,
            scale=1.1 * pulso,
            color=(255, 220, 235),
            alpha=210,
            glow=False
        )

        # Panel y mensaje final
        panel_rect = pygame.Rect(cx - 320, cy + 15, 640, 70)
        ProceduralUI.draw_panel(
            superficie, panel_rect,
            bg_color=(18, 8, 24, 210),
            border_color=config.COLOR_ENERGY,
            cut=14,
            glow=True
        )

        texto_sombra = self.font.render("SISTEMA RESTAURADO <3. CIERRA LA VENTANA.", True, (40, 0, 20))
        texto = self.font.render("SISTEMA RESTAURADO <3. CIERRA LA VENTANA.", True, config.COLOR_ENERGY)
        texto_rect = texto.get_rect(center=panel_rect.center)
        superficie.blit(texto_sombra, (texto_rect.x + 2, texto_rect.y + 2))
        superficie.blit(texto, texto_rect)

        self.bursts.draw(superficie)
