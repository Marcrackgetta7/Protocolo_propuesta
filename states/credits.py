import pygame
from states.base_state import BaseState
from utils.vfx import ScreenShake
from utils import audio 
from utils import save_manager # <--- Importado
import config

class Credits(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "MAIN_MENU" 
        self.shake = ScreenShake()
        self.fuente = pygame.font.SysFont("consolas", 22)
        
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

    def startup(self):
        # Silencio intencional durante los créditos — no se reproduce música
        audio.detener_musica()

    def manejar_eventos(self, evento):
        pass 

    def actualizar(self, dt):
        self.shake.actualizar(dt)
        if self.estado == "SCROLL":
            self.y_offset -= 35 * dt 
            
            if self.y_offset < - (len(self.textos) * 40):
                self.estado = "END"
                
        elif self.estado == "END":
            self.timer_final += dt
            if self.timer_final > 3.0:
                audio.detener_musica()
                # ¡DESBLOQUEA LA GALERÍA AL TERMINAR LOS CRÉDITOS!
                save_manager.guardar(8) 
                self.done = True 

    def dibujar(self, superficie):
        surf_temp = pygame.Surface((config.WIDTH, config.HEIGHT))
        surf_temp.fill(config.COLOR_BG)
        
        if self.estado == "SCROLL":
            y = self.y_offset
            for linea in self.textos:
                if linea != "":
                    color = config.COLOR_ENERGY if "amistad" in linea or "reparado" in linea else config.COLOR_TEXT
                    texto_surf = self.fuente.render(linea, True, color)
                    rect = texto_surf.get_rect(center=(config.WIDTH//2, int(y)))
                    surf_temp.blit(texto_surf, rect)
                y += 40
                
        ox, oy = self.shake.obtener_offset()
        superficie.blit(surf_temp, (ox, oy))