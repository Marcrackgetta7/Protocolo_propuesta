import pygame
from utils.fonts import get_font
from states.base_state import BaseState
from utils import save_manager
import config

class MainMenu(BaseState):
    def __init__(self):
        super().__init__()
        self.datos = save_manager.cargar()
        self.fuente_titulo = get_font(40, bold=True)
        self.fuente_botones = get_font(20)
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
        
        cx = config.WIDTH // 2
        
        if fase < 5:
            self.botones["Regalo 1: Nieve"] = {"rect": pygame.Rect(cx - 390, 195, 370, 48), "fase": 1, "destino": "INTRO_1"}
            self.botones["Regalo 2: Bosque"] = {"rect": pygame.Rect(cx - 390, 265, 370, 48), "fase": 2, "destino": "INTRO_2"}
            self.botones["Regalo 3: Entregas"] = {"rect": pygame.Rect(cx + 20, 195, 370, 48), "fase": 3, "destino": "INTRO_3"}
            self.botones["Regalo 4: El Jefe"] = {"rect": pygame.Rect(cx + 20, 265, 370, 48), "fase": 4, "destino": "INTRO_4"}
        elif fase < 8:
            self.botones["Brecha 1: Infiltración"] = {"rect": pygame.Rect(cx - 390, 195, 370, 48), "fase": 5, "destino": "INTRO"}
            self.botones["Brecha 2: Laberinto"] = {"rect": pygame.Rect(cx - 390, 265, 370, 48), "fase": 6, "destino": "INTRO_6"}
            self.botones["Brecha 3: El Núcleo"] = {"rect": pygame.Rect(cx + 20, 195, 370, 48), "fase": 7, "destino": "INTRO_7"}
            self.botones["Registro de Logros"] = {"rect": pygame.Rect(cx + 20, 265, 370, 48), "fase": 1, "destino": "ACHIEVEMENTS"}
        else:
            self.botones["Regalo 1: Nieve"] = {"rect": pygame.Rect(cx - 410, 165, 390, 42), "fase": 1, "destino": "INTRO_1"}
            self.botones["Regalo 2: Bosque"] = {"rect": pygame.Rect(cx - 410, 217, 390, 42), "fase": 2, "destino": "INTRO_2"}
            self.botones["Regalo 3: Entregas"] = {"rect": pygame.Rect(cx - 410, 269, 390, 42), "fase": 3, "destino": "INTRO_3"}
            self.botones["Regalo 4: El Jefe"] = {"rect": pygame.Rect(cx - 410, 321, 390, 42), "fase": 1, "destino": "INTRO_4"}
            self.botones["Brecha 1: Infiltración"] = {"rect": pygame.Rect(cx + 20, 165, 390, 42), "fase": 1, "destino": "INTRO"}
            self.botones["Brecha 2: Laberinto"] = {"rect": pygame.Rect(cx + 20, 217, 390, 42), "fase": 1, "destino": "INTRO_6"}
            self.botones["Brecha 3: El Núcleo"] = {"rect": pygame.Rect(cx + 20, 269, 390, 42), "fase": 1, "destino": "INTRO_7"}
            self.botones["Registro de Logros"] = {"rect": pygame.Rect(cx + 20, 321, 390, 42), "fase": 1, "destino": "ACHIEVEMENTS"}
            
            if len(secretos) >= self.TOTAL_LOGROS:
                self.botones["ARCHIVOS OCULTOS"] = {"rect": pygame.Rect(cx - 220, 385, 440, 44), "fase": 8, "destino": "GALLERY"}
            else:
                self.botones[f"FALTAN {self.TOTAL_LOGROS - len(secretos)} LOGROS"] = {"rect": pygame.Rect(cx - 220, 385, 440, 44), "fase": 99, "destino": "NONE"}
                
        # Botones inferiores con márgenes limpios
        self.botones["Configuración"] = {"rect": pygame.Rect(40, config.HEIGHT - 55, 200, 40), "fase": 1, "destino": "SETTINGS"}
        self.botones["Estadísticas"] = {"rect": pygame.Rect(config.WIDTH - 240, config.HEIGHT - 55, 200, 40), "fase": 1, "destino": "STATS"}

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
        superficie.blit(titulo_surf, titulo_surf.get_rect(center=(config.WIDTH//2, 55)))

        pasos_completados = min(fase_actual - 1, 7) + len(secretos)
        progreso = pasos_completados / 16.0
        if progreso > 1.0: progreso = 1.0
        
        pygame.draw.rect(superficie, (50, 50, 50), (config.WIDTH//2 - 320, 95, 640, 16))
        pygame.draw.rect(superficie, color_tema, (config.WIDTH//2 - 320, 95, int(640 * progreso), 16))
        txt_progreso = self.fuente_botones.render(f"Progreso Total del Sistema: {int(progreso * 100)}%", True, (255,255,255))
        superficie.blit(txt_progreso, txt_progreso.get_rect(center=(config.WIDTH//2, 125)))

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