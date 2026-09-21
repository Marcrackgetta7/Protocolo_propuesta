import pygame
from states.base_state import BaseState
from utils import save_manager
import config

LOGROS_DATA = [
    {"id": "L1", "tipo": "LOGRO", "nombre": "Manos Ágiles", "desc": "Fase 1: Atrapa los regalos. (Margen de error: Máximo 1 caída)."},
    {"id": "L2", "tipo": "LOGRO", "nombre": "Velocista Nevado", "desc": "Fase 2: Escapa del laberinto en menos de 15 segundos."},
    {"id": "L3", "tipo": "LOGRO", "nombre": "Santa Veloz", "desc": "Fase 3: Entrega todos los regalos y que te sobren 5+ segundos."},
    {"id": "L4", "tipo": "LOGRO", "nombre": "Sangre Caliente", "desc": "Fase 4: Vence al Muñeco de Nieve sin que tu barra de frío llegue a 100%."},
    {"id": "L5", "tipo": "LOGRO", "nombre": "Fantasma Digital", "desc": "Fase 5: Completa la infiltración sin que ningún láser te toque."},
    {"id": "L6", "tipo": "LOGRO", "nombre": "Fuerza Bruta", "desc": "Fase 6: Destruye al menos 3 cortafuegos del mapa antes de escapar."},
    {"id": "Pacifista", "tipo": "LOGRO", "nombre": "Pacifista", "desc": "Fase 7: Sobrevive 15 segundos de combate contra el Núcleo sin disparar."},
    {"id": "Estrella Helada", "tipo": "SECRETO", "nombre": "Estrella Helada", "desc": "Acertijo: En el bosque, busca la pared que no es pared antes de la luz final."},
    {"id": "Código Muerto", "tipo": "SECRETO", "nombre": "Código Muerto", "desc": "Acertijo: En el abismo del laberinto, la esquina inferior izquierda oculta un fantasma."}
]

class Achievements(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "MAIN_MENU"
        self.fuente_titulo = pygame.font.SysFont("consolas", 30, bold=True)
        self.fuente_nombre = pygame.font.SysFont("consolas", 18, bold=True)
        self.fuente_desc = pygame.font.SysFont("consolas", 14)
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

    def actualizar(self, dt):
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_UP]: self.scroll_y += 300 * dt
        if teclas[pygame.K_DOWN]: self.scroll_y -= 300 * dt
        
        if self.scroll_y > 0: self.scroll_y = 0
        min_scroll = -max(0, (len(LOGROS_DATA) * 65) - (config.HEIGHT - 200))
        if self.scroll_y < min_scroll: self.scroll_y = min_scroll

    def dibujar(self, superficie):
        superficie.fill(config.COLOR_BG)
        
        y_base = 120 + self.scroll_y
        secretos_obtenidos = self.datos.get("secretos", [])

        for item in LOGROS_DATA:
            desbloqueado = item["id"] in secretos_obtenidos
            rect_item = pygame.Rect(config.WIDTH//2 - 380, y_base, 760, 55)
            
            if desbloqueado:
                color_fondo = (20, 60, 20) if item["tipo"] == "LOGRO" else (60, 60, 20)
                color_borde = (50, 200, 50) if item["tipo"] == "LOGRO" else (255, 215, 0)
                estado_txt = "[ DESBLOQUEADO ]"
            else:
                color_fondo = (20, 20, 20)
                color_borde = (80, 80, 80)
                estado_txt = "[ BLOQUEADO ]"

            pygame.draw.rect(superficie, color_fondo, rect_item)
            pygame.draw.rect(superficie, color_borde, rect_item, 2)
            
            txt_nombre = self.fuente_nombre.render(f"{item['tipo']} - {item['nombre']}", True, color_borde)
            txt_desc = self.fuente_desc.render(item["desc"], True, (200, 200, 200))
            txt_estado = self.fuente_nombre.render(estado_txt, True, color_borde)

            superficie.blit(txt_nombre, (rect_item.x + 15, rect_item.y + 8))
            superficie.blit(txt_desc, (rect_item.x + 15, rect_item.y + 30))
            superficie.blit(txt_estado, (rect_item.right - 180, rect_item.y + 18))

            y_base += 65

        pygame.draw.rect(superficie, config.COLOR_BG, (0, 0, config.WIDTH, 100))
        tit = self.fuente_titulo.render("BASE DE DATOS: LOGROS Y SECRETOS", True, config.COLOR_ENERGY)
        superficie.blit(tit, tit.get_rect(center=(config.WIDTH//2, 40)))
        
        inst = self.fuente_desc.render(f"Progreso Total: {len(secretos_obtenidos)}/9  |  [ Usa las flechas/rueda para bajar | ESC para volver ]", True, (150,150,150))
        superficie.blit(inst, inst.get_rect(center=(config.WIDTH//2, 75)))
        pygame.draw.line(superficie, config.COLOR_ENERGY, (50, 100), (config.WIDTH - 50, 100), 2)