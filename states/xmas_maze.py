import pygame
import math
from states.base_state import BaseState
from entities.player import Player
from utils.companion import CompanionUI
from utils import audio
from utils import save_manager 
from utils.vfx import ScreenShake
import config

MAPA = [
    "111111111111111111111111",
    "1S0010000000001000000001",
    "101010111110101011111101",
    "100000000000101010000C01",
    "101111101111100010110101",
    "10000C100000111110100001",
    "111110111110000000101111",
    "100000000011111110100001",
    "101111111010000010111101",
    "10C000000010111010000C01",
    "101011111110101011110101",
    "10000000000010F*100000E1",
    "111111111111111111111111",
]

class Snowman:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.radio = 12
        self.velocidad = 50.0 
    def actualizar(self, dt, jugador_x, jugador_y):
        dx = jugador_x - self.x
        dy = jugador_y - self.y
        distancia = math.hypot(dx, dy)
        if distancia > 0:
            self.x += (dx / distancia) * self.velocidad * dt
            self.y += (dy / distancia) * self.velocidad * dt
    def dibujar(self, sup):
        pygame.draw.circle(sup, (255, 255, 255), (int(self.x), int(self.y)), self.radio)
        pygame.draw.circle(sup, (255, 255, 255), (int(self.x), int(self.y) - 12), self.radio - 4)

class XmasMaze(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "OUTRO_2"
        self.tam_celda = 40
        self.jugador = None
        self.compañero = CompanionUI()
        self.shake = ScreenShake()
        self.paredes = []
        self.paredes_falsas = []
        self.esferas = []
        self.snowmen = []
        self.salida = None
        self.secreto_rect = None
        self.esferas_recogidas = 0
        self.tiempo_jugado = 0.0
        self.tiempo_restante = 60.0
        self.ganado = False
        self.timer_victoria = 0.0
        self.fuente_ui = pygame.font.SysFont("consolas", 24, bold=True)

    def startup(self):
        self.paredes, self.paredes_falsas, self.esferas, self.snowmen = [], [], [], []
        self.esferas_recogidas, self.tiempo_jugado = 0, 0.0
        self.tiempo_restante = 60.0
        self.secreto_rect = None
        self.ganado, self.timer_victoria = False, 0.0
        
        self.logros_obtenidos = save_manager.cargar().get("secretos", [])
        ya_tiene_secreto = "Estrella Helada" in self.logros_obtenidos

        for fila in range(len(MAPA)):
            for col in range(len(MAPA[fila])):
                char = MAPA[fila][col]
                x, y = col * self.tam_celda, fila * self.tam_celda
                rect = pygame.Rect(x, y, self.tam_celda, self.tam_celda)
                if char == "1": self.paredes.append(rect)
                elif char == "F": self.paredes_falsas.append(rect)
                elif char == "*" and not ya_tiene_secreto: self.secreto_rect = rect 
                elif char == "C": self.esferas.append(rect)
                elif char == "S": self.jugador = Player(x + self.tam_celda//2, y + self.tam_celda//2)
                elif char == "E": self.salida = rect
                
        self.snowmen = [
            Snowman(800, 200),
            Snowman(300, 400)
        ]
                
        self.compañero.mostrar_mensaje("Bosque Nevado. Encuentra las 4 esferas para abrir el camino.")
        audio.reproducir_musica("assets/audio/Fase2_nav.ogg", volumen=0.4)

    def manejar_eventos(self, evento):
        pass

    def actualizar(self, dt):
        self.shake.actualizar(dt)
        self.compañero.actualizar(dt)
        
        if getattr(self, "game_over", False):
            self.timer_game_over += dt
            if self.timer_game_over > 2.0:
                self.game_over = False
                self.startup()
            return
            
        if self.ganado:
            self.timer_victoria += dt
            if self.timer_victoria > 1.5:
                save_manager.guardar(fase=3) 
                self.done = True
            return

        self.tiempo_jugado += dt
        self.tiempo_restante -= dt
        
        if self.tiempo_restante <= 0:
            self.tiempo_restante = 0
            if not getattr(self, "game_over", False):
                self.game_over = True
                self.timer_game_over = 0.0
                audio.reproducir("explosion")
                self.compañero.mostrar_mensaje("¡Se acabó el tiempo! Has quedado congelado.")
            return

        teclas = pygame.key.get_pressed()
        vel = self.jugador.velocidad * dt

        dx = 0
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]: dx -= 1
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: dx += 1
        self.jugador.x += dx * vel
        rect_jugador = pygame.Rect(self.jugador.x - 10, self.jugador.y - 10, 20, 20)
        for p in self.paredes:
            if rect_jugador.colliderect(p): self.jugador.x -= dx * vel; break

        dy = 0
        if teclas[pygame.K_UP] or teclas[pygame.K_w]: dy -= 1
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]: dy += 1
        self.jugador.y += dy * vel
        rect_jugador = pygame.Rect(self.jugador.x - 10, self.jugador.y - 10, 20, 20)
        for p in self.paredes:
            if rect_jugador.colliderect(p): self.jugador.y -= dy * vel; break

        for e in self.esferas[:]:
            if rect_jugador.colliderect(e):
                self.esferas.remove(e)
                self.esferas_recogidas += 1
                audio.reproducir("anomalia")
                if self.esferas_recogidas == 4:
                    self.compañero.mostrar_mensaje("¡Todas las esferas listas! Corre al portal verde.")

        if self.secreto_rect and rect_jugador.colliderect(self.secreto_rect):
            save_manager.guardar(secreto="Estrella Helada") 
            self.secreto_rect = None
            audio.reproducir("tecla")
            self.compañero.mostrar_mensaje("¡SECRETO DESCUBIERTO: Estrella Helada!")
            
        for sm in self.snowmen:
            sm.actualizar(dt, self.jugador.x, self.jugador.y)
            if math.hypot(self.jugador.x - sm.x, self.jugador.y - sm.y) < (self.jugador.radio_nucleo + sm.radio):
                if not getattr(self, "game_over", False):
                    self.game_over = True
                    self.timer_game_over = 0.0
                    self.shake.iniciar(10, 0.4)
                    audio.reproducir("explosion")
                    self.compañero.mostrar_mensaje("¡Te atrapó un muñeco de nieve!")

        if self.esferas_recogidas >= 4 and rect_jugador.colliderect(self.salida):
            self.ganado = True
            if self.tiempo_jugado < 15.0 and "L2" not in self.logros_obtenidos:
                save_manager.guardar(secreto="L2")
                self.compañero.mostrar_mensaje("¡LOGRO DESBLOQUEADO: Velocista Nevado (<15s)!")
                audio.reproducir("tecla")
            else:
                self.compañero.mostrar_mensaje("¡Nivel Completado! Avanzando...")

    def dibujar(self, superficie):
        surf_temp = pygame.Surface((config.WIDTH, config.HEIGHT))
        surf_temp.fill((20, 40, 60))
        for p in self.paredes + self.paredes_falsas:
            pygame.draw.rect(surf_temp, (150, 200, 255), p)
            pygame.draw.rect(surf_temp, (200, 230, 255), p, 2)
            
        for e in self.esferas: pygame.draw.circle(surf_temp, (255, 215, 0), e.center, 10)
            
        if self.secreto_rect:
            pygame.draw.rect(surf_temp, (255, 215, 0), self.secreto_rect)
            pygame.draw.rect(surf_temp, (255, 255, 255), self.secreto_rect, 2)
            
        color_salida = (50, 255, 50) if self.esferas_recogidas >= 4 else (255, 50, 50)
        pygame.draw.rect(surf_temp, color_salida, self.salida)
        
        for sm in self.snowmen: sm.dibujar(surf_temp)
        self.jugador.dibujar(surf_temp)
        
        txt_tiempo = self.fuente_ui.render(f"Tiempo: {max(0, self.tiempo_restante):.1f}s", True, (255, 255, 255))
        surf_temp.blit(txt_tiempo, (20, 20))
        
        ox, oy = self.shake.obtener_offset()
        superficie.blit(surf_temp, (ox, oy))
        
        if getattr(self, "game_over", False):
            overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 50, 50, 100))
            superficie.blit(overlay, (0, 0))
            fuente = pygame.font.SysFont("consolas", 40, bold=True)
            txt_over = fuente.render("CONGELADO", True, (255, 255, 255))
            superficie.blit(txt_over, txt_over.get_rect(center=(config.WIDTH//2, config.HEIGHT//2)))
            
        self.compañero.dibujar(superficie, self.jugador.y)