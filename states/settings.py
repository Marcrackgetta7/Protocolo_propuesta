import pygame
import os
from states.base_state import BaseState
from entities.ui_button import UIButton
from utils import save_manager, audio
import config

class Settings(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "MAIN_MENU"
        self.fuente_titulo = pygame.font.SysFont("consolas", 40, bold=True)
        self.fuente_texto = pygame.font.SysFont("consolas", 20)
        self.datos = save_manager.cargar()
        self.config_audio = self.datos.get("config", {"musica": 1.0, "sfx": 1.0})
        
        cx = config.WIDTH // 2
        self.btn_volver = UIButton(cx - 100, config.HEIGHT - 80, 200, 40, "Volver al Menú")
        self.btn_reset = UIButton(cx - 150, 400, 300, 40, "RESETEAR PROGRESO")
        self.btn_reset.color_normal = (60, 20, 20)
        self.btn_reset.color_hover = config.COLOR_DANGER
        
        self.rect_musica = pygame.Rect(cx - 150, 200, 300, 20)
        self.rect_sfx = pygame.Rect(cx - 150, 300, 300, 20)
        self.arrastrando_musica = False
        self.arrastrando_sfx = False
        self.confirmar_reset = False

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
                        shutil.copy(save_manager.ARCHIVO, save_manager.ARCHIVO + ".bak")
                    datos_limpios = {"fase_desbloqueada": 1, "secretos": [], "autenticado": True, "config": self.config_audio}
                    import json
                    with open(save_manager.ARCHIVO, "w") as f:
                        json.dump(datos_limpios, f)
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

    def dibujar(self, superficie):
        superficie.fill(config.COLOR_BG)
        
        tit = self.fuente_titulo.render("CONFIGURACIÓN DEL SISTEMA", True, config.COLOR_TEXT)
        superficie.blit(tit, tit.get_rect(center=(config.WIDTH//2, 80)))
        
        superficie.blit(self.fuente_texto.render(f"Volumen Música: {int(self.config_audio['musica']*100)}%", True, config.COLOR_TEXT), (self.rect_musica.x, self.rect_musica.y - 30))
        pygame.draw.rect(superficie, (50, 50, 50), self.rect_musica)
        pygame.draw.rect(superficie, config.COLOR_ENERGY, (self.rect_musica.x, self.rect_musica.y, int(self.rect_musica.width * self.config_audio["musica"]), self.rect_musica.height))
        pygame.draw.rect(superficie, (255, 255, 255), self.rect_musica, 2)
        
        superficie.blit(self.fuente_texto.render(f"Volumen Efectos (SFX): {int(self.config_audio['sfx']*100)}%", True, config.COLOR_TEXT), (self.rect_sfx.x, self.rect_sfx.y - 30))
        pygame.draw.rect(superficie, (50, 50, 50), self.rect_sfx)
        pygame.draw.rect(superficie, config.COLOR_ENERGY, (self.rect_sfx.x, self.rect_sfx.y, int(self.rect_sfx.width * self.config_audio["sfx"]), self.rect_sfx.height))
        pygame.draw.rect(superficie, (255, 255, 255), self.rect_sfx, 2)

        self.btn_volver.dibujar(superficie, pygame.mouse.get_pos())
        self.btn_reset.dibujar(superficie, pygame.mouse.get_pos())
