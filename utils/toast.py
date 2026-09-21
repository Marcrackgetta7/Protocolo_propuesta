import pygame
import config
from utils import audio

class ToastManager:
    _instancia = None
    
    @classmethod
    def get(cls):
        if cls._instancia is None:
            cls._instancia = ToastManager()
        return cls._instancia
        
    def __init__(self):
        self.toasts = [] # Lista de diccionarios con info del toast
        self.fuente_tit = None
        self.fuente_txt = None
        
    def mostrar(self, titulo, mensaje, duracion=4.0):
        if not pygame.font.get_init():
            return
            
        if self.fuente_tit is None:
            self.fuente_tit = pygame.font.SysFont("consolas", 20, bold=True)
            self.fuente_txt = pygame.font.SysFont("consolas", 16)
            
        self.toasts.append({
            "titulo": titulo,
            "mensaje": mensaje,
            "tiempo_restante": duracion,
            "tiempo_total": duracion,
            "y_offset": -100 # Empezar arriba de la pantalla (animación)
        })
        audio.reproducir("anomalia")

    def actualizar(self, dt):
        for t in self.toasts[:]:
            t["tiempo_restante"] -= dt
            
            # Animación de entrada
            if t["tiempo_restante"] > t["tiempo_total"] - 0.5:
                t["y_offset"] += (20 - t["y_offset"]) * 10 * dt
            # Animación de salida
            elif t["tiempo_restante"] < 0.5:
                t["y_offset"] += (-100 - t["y_offset"]) * 10 * dt
                
            if t["tiempo_restante"] <= 0:
                self.toasts.remove(t)

    def dibujar(self, superficie):
        for i, t in enumerate(self.toasts):
            rect_w, rect_h = 400, 70
            rect_x = config.WIDTH // 2 - rect_w // 2
            rect_y = int(t["y_offset"]) + (i * (rect_h + 10))
            
            # Dibujar caja
            pygame.draw.rect(superficie, (20, 20, 20), (rect_x, rect_y, rect_w, rect_h))
            pygame.draw.rect(superficie, config.COLOR_ENERGY, (rect_x, rect_y, rect_w, rect_h), 2)
            
            # Textos
            tit_surf = self.fuente_tit.render(t["titulo"], True, config.COLOR_ENERGY)
            msg_surf = self.fuente_txt.render(t["mensaje"], True, (255, 255, 255))
            
            superficie.blit(tit_surf, (rect_x + 15, rect_y + 10))
            superficie.blit(msg_surf, (rect_x + 15, rect_y + 35))
