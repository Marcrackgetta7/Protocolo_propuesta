import math
import pygame
from utils.fonts import get_font
from states.base_state import BaseState
from utils.text_renderer import TypewriterText
from utils import audio
from utils.vfx import (
    GlowCache,
    GradientCache,
    HeartRenderer,
    FloatingParticles,
    BurstPool,
    ProceduralUI,
)
from entities.ui_button import UIButton
import config


class Proposal(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "OUTRO"
        self.fuente_grande = get_font(28, bold=True)
        self.fuente_normal = get_font(24)

        self.rect_si = pygame.Rect(config.WIDTH // 2 - 180, 390, 150, 48)
        self.btn_no = UIButton(config.WIDTH // 2 + 30, 390, 150, 48, "[ NO ]", evasivo=True)

        self.escritor = None
        self.mostrar_botones = False
        self.error_no = False
        self.timer = 0.0
        self.timer_error = 0.0
        self.tiempo_anim = 0.0

        # Pre-cálculo de superficies y pools de partículas
        self.bg_surf = GradientCache.get_vertical(
            config.WIDTH, config.HEIGHT, (10, 4, 16), (28, 6, 22), vignette=True
        )
        self.particulas = FloatingParticles(count=48, mode="romantic")
        self.bursts = BurstPool(capacity=55)
        self.ultimo_pos_no = (self.btn_no.rect.centerx, self.btn_no.rect.centery)

    def startup(self):
        audio.detener_musica()

        # --- AQUÍ ESTÁ LA GRAN PREGUNTA ---
        texto_final = "SISTEMA RESTAURADO.\n\nTodo este protocolo fue creado para este momento.\nTengo una última pregunta para ti...\n\n¿Quieres ser mi novia?"

        self.escritor = TypewriterText(
            self.fuente_grande, texto_final, (config.WIDTH // 2 - 360, 90), speed=0.08, max_width=720
        )
        self.mostrar_botones = False
        self.error_no = False
        self.timer = 0.0
        self.timer_error = 0.0
        self.tiempo_anim = 0.0
        self.btn_no.intentos_evasion = 0
        self.btn_no.visible = True
        self.btn_no.texto = "[ NO ]"
        self.btn_no.rect.topleft = (config.WIDTH // 2 + 30, 390)
        self.ultimo_pos_no = (self.btn_no.rect.centerx, self.btn_no.rect.centery)

    def manejar_eventos(self, evento):
        clic_izq = (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1)
        if self.mostrar_botones and clic_izq:
            pos_raton = pygame.mouse.get_pos()

            if self.rect_si.collidepoint(pos_raton):
                audio.reproducir("anomalia")
                self.bursts.emit(self.rect_si.centerx, self.rect_si.centery, count=30, heart_chance=0.6)
                from utils import save_manager
                save_manager.guardar(answer_key="final", answer_val="SÍ")
                self.done = True

            elif self.btn_no.clic(pos_raton, clic_izq):
                audio.reproducir("explosion")
                self.error_no = True
                self.timer_error = 0.0

    def actualizar(self, dt):
        self.tiempo_anim += dt
        self.particulas.update(dt)
        self.bursts.update(dt)

        if self.escritor:
            self.escritor.actualizar(dt)
            if self.escritor.finished:
                self.timer += dt
                if self.timer > 2.0 and not self.error_no:
                    if not self.mostrar_botones:
                        self.bursts.emit(config.WIDTH // 2, 390, count=22, heart_chance=0.5)
                    self.mostrar_botones = True

        if self.mostrar_botones:
            prev_pos = (self.btn_no.rect.centerx, self.btn_no.rect.centery)
            self.btn_no.actualizar(pygame.mouse.get_pos())
            curr_pos = (self.btn_no.rect.centerx, self.btn_no.rect.centery)
            if prev_pos != curr_pos:
                # Efecto de chispa/glitch al teletransportarse el botón NO
                self.bursts.emit(
                    prev_pos[0], prev_pos[1],
                    count=12,
                    colors=[config.COLOR_DANGER, (255, 100, 140), (200, 200, 200)],
                    heart_chance=0.0,
                    speed_range=(60, 190)
                )
                self.ultimo_pos_no = prev_pos

        if self.error_no:
            self.timer_error += dt
            if self.timer_error > 2.0:
                self.error_no = False

    def dibujar(self, superficie):
        superficie.blit(self.bg_surf, (0, 0))
        self.particulas.draw(superficie)

        cx, cy = config.WIDTH // 2, config.HEIGHT // 2 - 20
        latido = 1.0 + 0.08 * math.sin(self.tiempo_anim * 3.2)

        # Halo ambiental y corazón geométrico latiendo detrás del panel
        GlowCache.blit(superficie, cx, cy, int(190 * latido), config.COLOR_ENERGY, intensity=0.28)
        HeartRenderer.draw(
            superficie, cx, cy - 10,
            scale=4.2 * latido,
            color=config.COLOR_ENERGY,
            alpha=35,
            width=2,
            glow=False
        )
        HeartRenderer.draw(
            superficie, cx, cy - 10,
            scale=2.8 * (2.0 - latido),
            color=(255, 140, 185),
            alpha=25,
            width=1,
            glow=False
        )

        # Marco traslúcido principal para la pregunta
        panel_rect = pygame.Rect(config.WIDTH // 2 - 400, 55, 800, 295)
        ProceduralUI.draw_panel(
            superficie, panel_rect,
            bg_color=(14, 8, 20, 185),
            border_color=config.COLOR_ENERGY,
            cut=16,
            glow=True
        )

        if self.escritor:
            self.escritor.dibujar(superficie)

        if self.mostrar_botones:
            pos_raton = pygame.mouse.get_pos()
            hover_si = self.rect_si.collidepoint(pos_raton)

            if hover_si:
                color_si = config.COLOR_ENERGY
                pulso_btn = 1.0 + 0.15 * math.sin(self.tiempo_anim * 8.0)
                GlowCache.blit(
                    superficie, self.rect_si.centerx, self.rect_si.centery,
                    int(68 * pulso_btn), config.COLOR_ENERGY, intensity=0.75
                )
                # Dos partículas orbitales alrededor del botón SÍ en hover
                for i in range(2):
                    ang = self.tiempo_anim * 4.5 + i * math.pi
                    ox = self.rect_si.centerx + math.cos(ang) * 84
                    oy = self.rect_si.centery + math.sin(ang) * 28
                    HeartRenderer.draw(superficie, ox, oy, scale=0.28, color=(255, 180, 210), alpha=220, glow=True)
            else:
                color_si = config.COLOR_TEXT
                GlowCache.blit(
                    superficie, self.rect_si.centerx, self.rect_si.centery,
                    50, config.COLOR_ENERGY, intensity=0.32
                )

            ProceduralUI.draw_panel(
                superficie, self.rect_si,
                bg_color=(45, 10, 28, 225) if hover_si else (24, 14, 28, 205),
                border_color=color_si,
                cut=8,
                glow=False
            )
            txt_si = self.fuente_normal.render("[ SÍ ]", True, color_si)
            superficie.blit(txt_si, txt_si.get_rect(center=self.rect_si.center))

            if self.error_no:
                GlowCache.blit(superficie, config.WIDTH // 2, 470, 90, config.COLOR_DANGER, intensity=0.45)
                txt_err = self.fuente_normal.render(
                    "Acción denegada por el administrador.", True, config.COLOR_DANGER
                )
                superficie.blit(txt_err, txt_err.get_rect(center=(config.WIDTH // 2, 470)))
            else:
                self.btn_no.dibujar(superficie, pos_raton)

        self.bursts.draw(superficie)
