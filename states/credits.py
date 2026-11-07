import pygame
from utils.fonts import get_font
from states.base_state import BaseState
from utils.vfx import ScreenShake, GlowCache, GradientCache, FloatingParticles
from utils import audio
from utils import save_manager
import config


class Credits(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "MAIN_MENU"
        self.shake = ScreenShake()
        self.fuente = get_font(22)

        self.textos = [
            "SISTEMA APAGADO CON ÉXITO.",
            "Recuperando fragmentos finales...",
            "",
            "A mi mejor amiga,",
            "Han sido casi 3 años de amistad...",
            "Soportando mis niveles de cafeína,",
            "Y aguantando a este enano.",
            "",
            "El sistema ha sido reparado.",
            "Nos vemos del otro lado.",
            "",
            "[ CONEXIÓN TERMINADA ]"
        ]
        self.y_offset = config.HEIGHT
        self.estado = "SCROLL"
        self.timer_final = 0.0

        self.bg_surf = GradientCache.get_vertical(
            config.WIDTH, config.HEIGHT, (6, 6, 12), (18, 6, 16), vignette=True
        )
        self.particulas = FloatingParticles(count=38, mode="romantic")

    def startup(self):
        self.done = False
        self.next_state = "MAIN_MENU"
        # Silencio intencional durante los créditos — no se reproduce música
        audio.detener_musica()
        self.y_offset = config.HEIGHT
        self.estado = "SCROLL"
        self.timer_final = 0.0

    def manejar_eventos(self, evento):
        pass

    def actualizar(self, dt):
        self.shake.actualizar(dt)
        self.particulas.update(dt)
        if self.estado == "SCROLL":
            self.y_offset -= 35 * dt

            if self.y_offset < -(len(self.textos) * 40):
                self.estado = "END"

        elif self.estado == "END":
            self.timer_final += dt
            if self.timer_final > 3.0:
                audio.detener_musica()
                # ¡DESBLOQUEA LA GALERÍA AL TERMINAR LOS CRÉDITOS!
                save_manager.guardar(8)
                self.done = True

    def dibujar(self, superficie):
        ox, oy = self.shake.obtener_offset()
        superficie.blit(self.bg_surf, (ox, oy))
        self.particulas.draw(superficie)

        if self.estado == "SCROLL":
            y = self.y_offset
            for linea in self.textos:
                if linea != "":
                    es_destacado = ("amistad" in linea or "reparado" in linea or "mejor amiga" in linea)
                    color = config.COLOR_ENERGY if es_destacado else config.COLOR_TEXT
                    cy = int(y) + oy
                    cx = config.WIDTH // 2 + ox
                    if es_destacado and 0 < cy < config.HEIGHT:
                        GlowCache.blit(superficie, cx, cy, 75, config.COLOR_ENERGY, intensity=0.28)
                    texto_surf = self.fuente.render(linea, True, color)
                    rect = texto_surf.get_rect(center=(cx, cy))
                    superficie.blit(texto_surf, rect)
                y += 40
