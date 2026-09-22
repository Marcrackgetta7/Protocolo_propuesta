import pygame
from states.base_state import BaseState
from utils import save_manager
import config

class Stats(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "MAIN_MENU"
        self.fuente_titulo = pygame.font.SysFont("consolas", 30, bold=True)
        self.fuente_normal = pygame.font.SysFont("consolas", 20)
        self.fuente_fases = pygame.font.SysFont("consolas", 18)
        self.datos = save_manager.cargar()
        self.scroll_y = 0

    def startup(self):
        self.datos = save_manager.cargar()
        self.scroll_y = 0

    def manejar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self.done = True
        if evento.type == pygame.MOUSEWHEEL:
            self.scroll_y += evento.y * 30

    def formatear_tiempo(self, segundos):
        s = int(segundos)
        m = s // 60
        s = s % 60
        return f"{m:02d}:{s:02d}"

    def actualizar(self, dt):
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_UP]: self.scroll_y += 300 * dt
        if teclas[pygame.K_DOWN]: self.scroll_y -= 300 * dt
        
        if self.scroll_y > 0: self.scroll_y = 0

    def dibujar(self, superficie):
        superficie.fill(config.COLOR_BG)
        
        y_base = 120 + self.scroll_y
        
        times = self.datos.get("times", {})
        total_time = times.get("total", 0.0)
        time_100 = times.get("100_percent", 0.0)
        phases = times.get("phases", {})
        secretos_obtenidos = self.datos.get("secretos", [])
        
        # Bloque de Estadisticas Globales
        rect_global = pygame.Rect(config.WIDTH//2 - 380, y_base, 760, 100)
        pygame.draw.rect(superficie, (20, 30, 40), rect_global)
        pygame.draw.rect(superficie, config.COLOR_ENERGY, rect_global, 2)
        
        txt_total = self.fuente_normal.render(f"Tiempo Total de Juego: {self.formatear_tiempo(total_time)}", True, (255, 255, 255))
        superficie.blit(txt_total, (rect_global.x + 20, rect_global.y + 20))
        
        if time_100 > 0.0:
            txt_100 = self.fuente_normal.render(f"Tiempo para 100% Completado: {self.formatear_tiempo(time_100)}", True, (50, 255, 50))
        else:
            txt_100 = self.fuente_normal.render(f"Tiempo para 100% Completado: [No conseguido]", True, (100, 100, 100))
        superficie.blit(txt_100, (rect_global.x + 20, rect_global.y + 60))
        
        y_base += 130
        
        # Bloque de Fases
        fases_ordenadas = ["XMAS_MINIGAME", "XMAS_MAZE", "XMAS_DELIVERY", "XMAS_BOSS", "MINIGAME", "HACK_MAZE", "HACK_BOSS"]
        nombres_amigables = {
            "XMAS_MINIGAME": "Fase 1: Atrapando Regalos",
            "XMAS_MAZE": "Fase 2: Bosque Nevado",
            "XMAS_DELIVERY": "Fase 3: Entrega Nocturna",
            "XMAS_BOSS": "Fase 4: El Muñeco Gruñón",
            "MINIGAME": "Fase 5: Infiltración",
            "HACK_MAZE": "Fase 6: Laberinto de Cortafuegos",
            "HACK_BOSS": "Fase 7: El Núcleo"
        }
        
        for fase_clave in fases_ordenadas:
            if fase_clave in phases:
                rect_item = pygame.Rect(config.WIDTH//2 - 380, y_base, 760, 40)
                pygame.draw.rect(superficie, (20, 20, 20), rect_item)
                pygame.draw.rect(superficie, (80, 80, 80), rect_item, 1)
                
                nombre = nombres_amigables.get(fase_clave, fase_clave)
                tiempo = self.formatear_tiempo(phases[fase_clave])
                
                txt_nombre = self.fuente_fases.render(nombre, True, (200, 200, 200))
                txt_tiempo = self.fuente_fases.render(f"{tiempo}", True, config.COLOR_ENERGY)
                
                superficie.blit(txt_nombre, (rect_item.x + 15, rect_item.y + 10))
                superficie.blit(txt_tiempo, (rect_item.right - 100, rect_item.y + 10))
                
                y_base += 50
                
        # Limite de scroll
        min_scroll = -max(0, y_base - self.scroll_y - config.HEIGHT + 50)
        if self.scroll_y < min_scroll: self.scroll_y = min_scroll

        # Header fijo
        pygame.draw.rect(superficie, config.COLOR_BG, (0, 0, config.WIDTH, 100))
        tit = self.fuente_titulo.render("ESTADÍSTICAS DEL SISTEMA", True, config.COLOR_ENERGY)
        superficie.blit(tit, tit.get_rect(center=(config.WIDTH//2, 40)))
        
        inst = self.fuente_fases.render(f"Secretos Descubiertos: {len(secretos_obtenidos)}/9  |  [ ESC para volver ]", True, (150, 150, 150))
        superficie.blit(inst, inst.get_rect(center=(config.WIDTH//2, 75)))
        pygame.draw.line(superficie, config.COLOR_ENERGY, (50, 100), (config.WIDTH - 50, 100), 2)
