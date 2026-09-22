import pygame
from states.base_state import BaseState
from utils import save_manager
import config

class MainMenu(BaseState):
    def __init__(self):
        super().__init__()
        self.datos = save_manager.cargar()
        self.fuente_titulo = pygame.font.SysFont("consolas", 40, bold=True)
        self.fuente_botones = pygame.font.SysFont("consolas", 20)
        self.TOTAL_LOGROS = 9
        self.TOTAL_FASES = 8
        self.actualizar_botones()

    def startup(self):
        self.datos = save_manager.cargar()
        self.actualizar_botones()

    def actualizar_botones(self):
        fase = self.datos.get("fase_desbloqueada", 1)
        secretos = self.datos.get("secretos", [])
        self.botones = {}
        
        if fase < 5:
            self.botones["Regalo 1: Nieve"] = {"rect": pygame.Rect(config.WIDTH//2 - 150, 230, 300, 40), "fase": 1, "destino": "INTRO_1"}
            self.botones["Regalo 2: Bosque"] = {"rect": pygame.Rect(config.WIDTH//2 - 150, 290, 300, 40), "fase": 2, "destino": "INTRO_2"}
            self.botones["Regalo 3: Entregas"] = {"rect": pygame.Rect(config.WIDTH//2 - 150, 350, 300, 40), "fase": 3, "destino": "INTRO_3"}
            self.botones["Regalo 4: El Jefe"] = {"rect": pygame.Rect(config.WIDTH//2 - 150, 410, 300, 40), "fase": 4, "destino": "INTRO_4"}
        elif fase < 8:
            self.botones["Brecha 1: Infiltración"] = {"rect": pygame.Rect(config.WIDTH//2 - 150, 230, 300, 40), "fase": 5, "destino": "INTRO"}
            self.botones["Brecha 2: Laberinto"] = {"rect": pygame.Rect(config.WIDTH//2 - 150, 290, 300, 40), "fase": 6, "destino": "INTRO_6"}
            self.botones["Brecha 3: El Núcleo"] = {"rect": pygame.Rect(config.WIDTH//2 - 150, 350, 300, 40), "fase": 7, "destino": "INTRO_7"}
            self.botones["Registro de Logros"] = {"rect": pygame.Rect(config.WIDTH//2 - 150, 410, 300, 40), "fase": 1, "destino": "ACHIEVEMENTS"}
        else:
            self.botones["Regalo 1: Nieve"] = {"rect": pygame.Rect(config.WIDTH//2 - 320, 230, 300, 40), "fase": 1, "destino": "INTRO_1"}
            self.botones["Regalo 2: Bosque"] = {"rect": pygame.Rect(config.WIDTH//2 - 320, 290, 300, 40), "fase": 1, "destino": "INTRO_2"}
            self.botones["Regalo 3: Entregas"] = {"rect": pygame.Rect(config.WIDTH//2 - 320, 350, 300, 40), "fase": 1, "destino": "INTRO_3"}
            self.botones["Regalo 4: El Jefe"] = {"rect": pygame.Rect(config.WIDTH//2 - 320, 410, 300, 40), "fase": 1, "destino": "INTRO_4"}
            self.botones["Brecha 1: Infiltración"] = {"rect": pygame.Rect(config.WIDTH//2 + 20, 230, 300, 40), "fase": 1, "destino": "INTRO"}
            self.botones["Brecha 2: Laberinto"] = {"rect": pygame.Rect(config.WIDTH//2 + 20, 290, 300, 40), "fase": 1, "destino": "INTRO_6"}
            self.botones["Brecha 3: El Núcleo"] = {"rect": pygame.Rect(config.WIDTH//2 + 20, 350, 300, 40), "fase": 1, "destino": "INTRO_7"}
            self.botones["Registro de Logros"] = {"rect": pygame.Rect(config.WIDTH//2 + 20, 410, 300, 40), "fase": 1, "destino": "ACHIEVEMENTS"}
            
            if len(secretos) >= self.TOTAL_LOGROS:
                self.botones["ARCHIVOS OCULTOS"] = {"rect": pygame.Rect(config.WIDTH//2 - 150, 470, 300, 40), "fase": 8, "destino": "GALLERY"}
            else:
                self.botones[f"FALTAN {self.TOTAL_LOGROS - len(secretos)} LOGROS"] = {"rect": pygame.Rect(config.WIDTH//2 - 150, 470, 300, 40), "fase": 99, "destino": "NONE"}
                
        # Botones inferiores
        self.botones["Configuración"] = {"rect": pygame.Rect(10, config.HEIGHT - 50, 180, 40), "fase": 1, "destino": "SETTINGS"}
        self.botones["Estadísticas"] = {"rect": pygame.Rect(config.WIDTH - 190, config.HEIGHT - 50, 180, 40), "fase": 1, "destino": "STATS"}

    def manejar_eventos(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos_raton = pygame.mouse.get_pos()
            for nombre, info in self.botones.items():
                if info["rect"].collidepoint(pos_raton):
                    if self.datos.get("fase_desbloqueada", 1) >= info["fase"]:
                        self.next_state = info["destino"]
                        self.done = True
                    else:
                        from utils import audio
                        audio.reproducir("explosion") # Feedback de botón bloqueado

    def actualizar(self, dt): pass

    def dibujar(self, superficie):
        fase_actual = self.datos.get("fase_desbloqueada", 1)
        secretos = self.datos.get("secretos", [])
        
        if fase_actual < 5:
            superficie.fill((15, 35, 20)) 
            color_tema = (255, 100, 100) 
            titulo_texto = "UN CUENTO DE NAVIDAD"
        elif fase_actual < 8:
            superficie.fill(config.COLOR_BG) 
            color_tema = config.COLOR_DANGER 
            titulo_texto = "SISTEMA COMPROMETIDO"
        else:
            superficie.fill(config.COLOR_BG)
            color_tema = config.COLOR_ENERGY
            titulo_texto = "PROTOCOLO: COMPLETADO"
            
        titulo_surf = self.fuente_titulo.render(titulo_texto, True, color_tema)
        superficie.blit(titulo_surf, titulo_surf.get_rect(center=(config.WIDTH//2, 100)))

        pasos_completados = min(fase_actual - 1, 7) + len(secretos)
        progreso = pasos_completados / 16.0
        if progreso > 1.0: progreso = 1.0
        
        pygame.draw.rect(superficie, (50, 50, 50), (config.WIDTH//2 - 250, 150, 500, 20))
        pygame.draw.rect(superficie, color_tema, (config.WIDTH//2 - 250, 150, int(500 * progreso), 20))
        txt_progreso = self.fuente_botones.render(f"Progreso Total del Sistema: {int(progreso * 100)}%", True, (255,255,255))
        superficie.blit(txt_progreso, txt_progreso.get_rect(center=(config.WIDTH//2, 185)))

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
                
            if "ARCHIVOS OCULTOS" in nombre: color_boton = config.COLOR_ENERGY
            elif "Registro de" in nombre: color_boton = (100, 100, 50)
                
            pygame.draw.rect(superficie, color_boton, rect)
            pygame.draw.rect(superficie, color_texto, rect, 2) 
            
            texto_surf = self.fuente_botones.render(nombre, True, color_texto)
            superficie.blit(texto_surf, texto_surf.get_rect(center=rect.center))