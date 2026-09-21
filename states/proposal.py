import pygame
from states.base_state import BaseState
from utils.text_renderer import TypewriterText
from utils import audio
import config

class Proposal(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "OUTRO"
        self.fuente_grande = pygame.font.SysFont("consolas", 28, bold=True)
        self.fuente_normal = pygame.font.SysFont("consolas", 24)
        
        self.rect_si = pygame.Rect(config.WIDTH//2 - 200, 450, 150, 50)
        self.rect_no = pygame.Rect(config.WIDTH//2 + 50, 450, 150, 50)
        
        self.escritor = None
        self.mostrar_botones = False
        self.error_no = False
        self.timer = 0.0
        self.timer_error = 0.0

    def startup(self):
        audio.detener_musica()
        
        # --- AQUÍ ESTÁ LA GRAN PREGUNTA ---
        texto_final = "SISTEMA RESTAURADO.\n\nTodo este protocolo fue creado para este momento.\nTengo una última pregunta para ti...\n\n¿Quieres ser mi novia?"
        
        self.escritor = TypewriterText(self.fuente_grande, texto_final, (config.WIDTH//2 - 380, 150), speed=0.08)
        self.mostrar_botones = False
        self.error_no = False
        self.timer = 0.0
        self.timer_error = 0.0

    def manejar_eventos(self, evento):
        if self.mostrar_botones and evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos_raton = pygame.mouse.get_pos()
            
            if self.rect_si.collidepoint(pos_raton):
                audio.reproducir("anomalia") 
                self.done = True
                
            elif self.rect_no.collidepoint(pos_raton):
                audio.reproducir("explosion")
                self.error_no = True
                self.timer_error = 0.0

    def actualizar(self, dt):
        if self.escritor:
            self.escritor.actualizar(dt)
            if self.escritor.finished:
                self.timer += dt
                if self.timer > 2.0 and not self.error_no:
                    self.mostrar_botones = True
                    
        if self.error_no:
            self.timer_error += dt
            if self.timer_error > 2.0:
                self.error_no = False

    def dibujar(self, superficie):
        superficie.fill((5, 5, 5))
        
        if self.escritor:
            self.escritor.dibujar(superficie)
            
        if self.mostrar_botones:
            pos_raton = pygame.mouse.get_pos()
            
            if self.rect_si.collidepoint(pos_raton):
                color_si = config.COLOR_ENERGY
            else:
                color_si = config.COLOR_TEXT
                
            pygame.draw.rect(superficie, color_si, self.rect_si, 2)
            txt_si = self.fuente_normal.render("[ SÍ ]", True, color_si)
            superficie.blit(txt_si, txt_si.get_rect(center=self.rect_si.center))
            
            if self.error_no:
                pygame.draw.rect(superficie, config.COLOR_DANGER, self.rect_no, 2)
                txt_no = self.fuente_normal.render("ERROR", True, config.COLOR_DANGER)
            else:
                if self.rect_no.collidepoint(pos_raton):
                    color_no = (100, 100, 100)
                else:
                    color_no = config.COLOR_TEXT
                pygame.draw.rect(superficie, color_no, self.rect_no, 2)
                txt_no = self.fuente_normal.render("[ NO ]", True, color_no)
                
            superficie.blit(txt_no, txt_no.get_rect(center=self.rect_no.center))
            
            if self.error_no:
                txt_err = self.fuente_normal.render("Acción denegada por el administrador.", True, config.COLOR_DANGER)
                superficie.blit(txt_err, txt_err.get_rect(center=(config.WIDTH//2, 550)))