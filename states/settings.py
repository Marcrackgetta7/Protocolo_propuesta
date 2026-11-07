import os
import pygame
from utils.fonts import get_font
from states.base_state import BaseState
from entities.ui_button import UIButton
from utils import save_manager, audio
from utils.vfx import GlowCache, GradientCache, ProceduralUI
import config


class Settings(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "MAIN_MENU"
        self.fuente_titulo = get_font(40, bold=True)
        self.fuente_texto = get_font(20)
        self.datos = save_manager.cargar()
        self.config_audio = self.datos.get("config", {"musica": 1.0, "sfx": 1.0})

        cx = config.WIDTH // 2
        self.btn_volver = UIButton(cx - 110, config.HEIGHT - 65, 220, 42, "Volver al Menú")
        self.btn_reset = UIButton(cx - 160, 345, 320, 42, "RESETEAR PROGRESO")
        self.btn_reset.color_normal = (60, 20, 20)
        self.btn_reset.color_hover = config.COLOR_DANGER

        self.rect_musica = pygame.Rect(cx - 160, 160, 320, 20)
        self.rect_sfx = pygame.Rect(cx - 160, 250, 320, 20)
        self.arrastrando_musica = False
        self.arrastrando_sfx = False
        self.confirmar_reset = False

        self.bg_surf = GradientCache.get_vertical(
            config.WIDTH, config.HEIGHT, (8, 10, 18), (18, 8, 16), vignette=True
        )
        self.panel_central = pygame.Rect(cx - 240, 105, 480, 305)

    def startup(self):
        self.done = False
        self.next_state = "MAIN_MENU"
        self.datos = save_manager.cargar()
        self.config_audio = self.datos.get("config", {"musica": 1.0, "sfx": 1.0})
        self.arrastrando_musica = False
        self.arrastrando_sfx = False
        self.confirmar_reset = False
        self.btn_reset.texto = "RESETEAR PROGRESO"

    def manejar_eventos(self, evento):
        clic_izq = (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1)
        pos_raton = pygame.mouse.get_pos()

        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self.done = True

        if clic_izq:
            if self.btn_volver.clic(pos_raton, clic_izq):
                save_manager.guardar(config_audio=self.config_audio)
                self.done = True

            elif self.btn_reset.clic(pos_raton, clic_izq):
                if not self.confirmar_reset:
                    audio.reproducir("explosion")
                    self.confirmar_reset = True
                    self.btn_reset.texto = "¿SEGURO? CLIC PARA CONFIRMAR"
                else:
                    audio.reproducir("explosion")
                    if os.path.exists(save_manager.ARCHIVO):
                        import shutil
                        try:
                            shutil.copy(save_manager.ARCHIVO, save_manager.ARCHIVO + ".bak")
                        except Exception:
                            pass
                    save_manager.reiniciar_partida(mantener_config=True)
                    self.done = True

            if self.rect_musica.collidepoint(pos_raton):
                self.arrastrando_musica = True
            elif self.rect_sfx.collidepoint(pos_raton):
                self.arrastrando_sfx = True

        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            self.arrastrando_musica = False
            self.arrastrando_sfx = False
            save_manager.guardar(config_audio=self.config_audio)

        if self.arrastrando_musica:
            vol = max(0.0, min(1.0, (pos_raton[0] - self.rect_musica.x) / self.rect_musica.width))
            self.config_audio["musica"] = vol
            audio.actualizar_volumenes(vol, self.config_audio["sfx"])

        elif self.arrastrando_sfx:
            vol = max(0.0, min(1.0, (pos_raton[0] - self.rect_sfx.x) / self.rect_sfx.width))
            self.config_audio["sfx"] = vol
            audio.actualizar_volumenes(self.config_audio["musica"], vol)

    def actualizar(self, dt):
        pos_raton = pygame.mouse.get_pos()
        self.btn_volver.actualizar(pos_raton)
        self.btn_reset.actualizar(pos_raton)

    def _dibujar_slider(self, superficie, rect, valor, etiqueta):
        superficie.blit(
            self.fuente_texto.render(f"{etiqueta}: {int(valor * 100)}%", True, config.COLOR_TEXT),
            (rect.x, rect.y - 30)
        )
        pygame.draw.rect(superficie, (30, 28, 40), rect)
        fill_w = int(rect.width * valor)
        if fill_w > 0:
            pygame.draw.rect(superficie, config.COLOR_ENERGY, (rect.x, rect.y, fill_w, rect.height))
        pygame.draw.rect(superficie, (220, 220, 235), rect, 2)

        # Nodo deslizador luminoso
        knob_x = rect.x + fill_w
        knob_y = rect.centery
        GlowCache.blit(superficie, knob_x, knob_y, 18, config.COLOR_ENERGY, intensity=0.65)
        pygame.draw.circle(superficie, (255, 255, 255), (knob_x, knob_y), 8)
        pygame.draw.circle(superficie, config.COLOR_ENERGY, (knob_x, knob_y), 4)

    def dibujar(self, superficie):
        superficie.blit(self.bg_surf, (0, 0))

        GlowCache.blit(superficie, config.WIDTH // 2, 55, 120, config.COLOR_ENERGY, intensity=0.28)
        tit = self.fuente_titulo.render("CONFIGURACIÓN DEL SISTEMA", True, config.COLOR_TEXT)
        superficie.blit(tit, tit.get_rect(center=(config.WIDTH // 2, 55)))

        ProceduralUI.draw_panel(
            superficie, self.panel_central,
            bg_color=(16, 12, 24, 210),
            border_color=config.COLOR_ENERGY,
            cut=14,
            glow=True
        )

        self._dibujar_slider(superficie, self.rect_musica, self.config_audio["musica"], "Volumen Música")
        self._dibujar_slider(superficie, self.rect_sfx, self.config_audio["sfx"], "Volumen Efectos (SFX)")

        pos_raton = pygame.mouse.get_pos()
        self.btn_volver.dibujar(superficie, pos_raton)
        self.btn_reset.dibujar(superficie, pos_raton)
