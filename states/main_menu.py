import pygame
from states.base_state import BaseState
from utils import save_manager
import config

class MainMenu(BaseState):
    def __init__(self):
        super().__init__()
        self.datos = save_manager.cargar()
        self.fuente_titulo = pygame.font.SysFont("consolas", 40, bold=True)
        self.fuente_botones = pygame.font.SysFont("consolas", 24)
        
        self.botones = {
            "Fase 1: Infiltración": {"rect": pygame.Rect(config.WIDTH//2 - 150, 250, 300, 50), "fase": 1, "destino": "INTRO"},
            "Fase 2: Laberinto Corrupto": {"rect": pygame.Rect(config.WIDTH//2 - 150, 320, 300, 50), "fase": 2, "destino": "INTER_1"},
            "Fase 3: El Núcleo": {"rect": pygame.Rect(config.WIDTH//2 - 150, 390, 300, 50), "fase": 3, "destino": "INTER_2"}
        }

    def startup(self):
        self.datos = save_manager.cargar()
        if self.datos["fase_desbloqueada"] >= 4 and "ARCHIVOS OCULTOS" not in self.botones:
            # AHORA APUNTA A LA GALERÍA
            self.botones["ARCHIVOS OCULTOS"] = {"rect": pygame.Rect(config.WIDTH//2 - 150, 500, 300, 50), "fase": 4, "destino": "GALLERY"}

    def manejar_eventos(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos_raton = pygame.mouse.get_pos()
            for nombre, info in self.botones.items():
                if info["rect"].collidepoint(pos_raton):
                    if self.datos["fase_desbloqueada"] >= info["fase"]:
                        self.next_state = info["destino"]
                        self.done = True

    def actualizar(self, dt): pass

    def dibujar(self, superficie):
        superficie.fill(config.COLOR_BG)
        fase_actual = self.datos["fase_desbloqueada"]
        
        color_tema = config.COLOR_DANGER if fase_actual >= 4 else config.COLOR_TEXT
        titulo_texto = "PROTOCOLO: BRECHA" if fase_actual < 4 else "SISTEMA COMPROMETIDO"
        
        titulo_surf = self.fuente_titulo.render(titulo_texto, True, color_tema)
        superficie.blit(titulo_surf, titulo_surf.get_rect(center=(config.WIDTH//2, 100)))

        progreso = (fase_actual - 1) / 4.0
        if progreso > 1.0: progreso = 1.0
        
        pygame.draw.rect(superficie, (50, 50, 50), (config.WIDTH//2 - 200, 160, 400, 20))
        pygame.draw.rect(superficie, color_tema, (config.WIDTH//2 - 200, 160, int(400 * progreso), 20))
        txt_progreso = self.fuente_botones.render(f"Progreso del Sistema: {int(progreso * 100)}%", True, (150, 150, 150))
        superficie.blit(txt_progreso, txt_progreso.get_rect(center=(config.WIDTH//2, 195)))

        pos_raton = pygame.mouse.get_pos()
        for nombre, info in self.botones.items():
            rect = info["rect"]
            desbloqueado = fase_actual >= info["fase"]
            
            if not desbloqueado:
                color_boton = (30, 30, 30) 
                color_texto = (100, 100, 100)
            elif rect.collidepoint(pos_raton):
                color_boton = (80, 80, 80) 
                color_texto = (255, 255, 255)
            else:
                color_boton = (50, 50, 50) 
                color_texto = config.COLOR_TEXT
                
            if nombre == "ARCHIVOS OCULTOS":
                color_boton = config.COLOR_DANGER
                color_texto = (255, 255, 255)
                
            pygame.draw.rect(superficie, color_boton, rect)
            pygame.draw.rect(superficie, color_texto, rect, 2) 
            
            texto_surf = self.fuente_botones.render(nombre, True, color_texto)
            superficie.blit(texto_surf, texto_surf.get_rect(center=rect.center))