import pygame
import math
from states.base_state import BaseState
from entities.player import Player
from entities.monster import Monster
from utils.light_mask import LightMask
from utils.companion import CompanionUI
from utils.vfx import ScreenShake
from utils import audio
from utils import save_manager 
import config

MAPA = [
    "111111111111111111111111",
    "1S0010002000001000000001",
    "101010111110101011111101",
    "102000000020101010000101",
    "101111101111100010110101",
    "100000100000111110100001",
    "111110111110000020101111",
    "100000000011111110100001",
    "101111111010000010111101",
    "101000002010111010000101",
    "101011111110101011110101",
    "1*F0000000001020000000E1",
    "111111111111111111111111",
]

class Maze(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "OUTRO_6" 
        self.tam_celda = 40 
        self.jugador = None
        self.monstruos = []
        self.mascara = LightMask()
        self.compañero = CompanionUI()
        self.shake = ScreenShake()
        self.paredes, self.paredes_falsas, self.cortafuegos = [], [], []
        self.salida, self.secreto_rect = None, None
        
        self.timer_hackeo = 0
        self.hackeando = False
        self.cortafuegos_actual = None
        
        self.cortafuegos_rotos = 0
        self.ganado, self.timer_victoria = False, 0.0

    def startup(self):
        self.paredes, self.paredes_falsas, self.cortafuegos, self.monstruos = [], [], [], []
        self.hackeando, self.ganado, self.timer_victoria = False, False, 0.0
        self.cortafuegos_rotos = 0
        self.secreto_rect = None
        
        self.logros_obtenidos = save_manager.cargar().get("secretos", [])
        ya_tiene_secreto = "Código Muerto" in self.logros_obtenidos
        for fila in range(len(MAPA)):
            for col in range(len(MAPA[fila])):
                char = MAPA[fila][col]
                x, y = col * self.tam_celda, fila * self.tam_celda
                rect = pygame.Rect(x, y, self.tam_celda, self.tam_celda)
                
                if char == "1": self.paredes.append(rect)
                elif char == "F": self.paredes_falsas.append(rect)
                elif char == "2": self.cortafuegos.append(rect)
                elif char == "E": self.salida = rect
        self.fase_oscura = True
        self.es_partida = True
        
        # Secretos
        self.secreto_encontrado = False
        self.logros_obtenidos = save_manager.cargar().get("secretos", [])

    def startup(self):
        self.jugador = Player(100, 100)
        self.monstruos = [
            Monster(500, 200),
            Monster(700, 400),
            Monster(200, 400)
        ]
        
        self.zonas_hackeo = [
            pygame.Rect(800, 100, 50, 50),
            pygame.Rect(400, 400, 50, 50)
        ]
        self.hackeos_completados = [False, False]
        self.tiempo_hackeando = [0.0, 0.0]
        
        # El secreto está en una esquina del laberinto (esquina superior derecha, pero un poco oculta)
        self.zona_secreto = pygame.Rect(850, 50, 30, 30) 
        self.secreto_encontrado = "fase2_secreto1" in save_manager.cargar().get("secretos", [])

        self.compañero.mostrar_mensaje("La visibilidad es nula. Hackea los terminales verdes para encender las luces.", id_voz="v_f2_in")
        audio.reproducir_musica("assets/audio/Fase2_dark.ogg", volumen=0.3)

    def manejar_eventos(self, evento):
        pass

    def actualizar(self, dt):
        self.shake.actualizar(dt)
        self.compañero.actualizar(dt)
        
        if self.ganado:
            self.timer_victoria += dt
            if self.timer_victoria > 2.5:
                save_manager.guardar(fase=7) 
                self.done = True
            return

        teclas = pygame.key.get_pressed()
        vel = self.jugador.velocidad * dt
        dx = 0
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]: dx -= 1
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: dx += 1
        self.jugador.x += dx * vel
        rect_jugador = pygame.Rect(self.jugador.x - 10, self.jugador.y - 10, 20, 20)
        for p in self.paredes + self.cortafuegos:
            if rect_jugador.colliderect(p): self.jugador.x -= dx * vel; break

        dy = 0
        if teclas[pygame.K_UP] or teclas[pygame.K_w]: dy -= 1
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]: dy += 1
        self.jugador.y += dy * vel
        rect_jugador = pygame.Rect(self.jugador.x - 10, self.jugador.y - 10, 20, 20)
        for p in self.paredes + self.cortafuegos:
            if rect_jugador.colliderect(p): self.jugador.y -= dy * vel; break

        for m in self.monstruos: m.actualizar(dt, self.jugador.x, self.jugador.y)

        if self.secreto_rect and rect_jugador.colliderect(self.secreto_rect):
            save_manager.guardar(secreto="Código Muerto")
            self.secreto_rect = None
            audio.reproducir("tecla")
            self.compañero.mostrar_mensaje("¡SECRETO ENCONTRADO: Código Muerto!")

        if not self.hackeando:
            for cf in self.cortafuegos:
                if math.hypot(self.jugador.x - (cf.x + 30), self.jugador.y - (cf.y + 30)) < 45:
                    self.hackeando, self.cortafuegos_actual, self.timer_hackeo = True, cf, 0.8 
                    self.compañero.mostrar_mensaje("¡Bloqueo! Dame un segundo, derribando cortafuegos...")
                    break
        else:
            dist_cancel = math.hypot(self.jugador.x - (self.cortafuegos_actual.x + 30), self.jugador.y - (self.cortafuegos_actual.y + 30))
            if dist_cancel > 60:
                self.hackeando = False 
                self.compañero.mostrar_mensaje("Conexión perdida. ¡Te alejaste demasiado de la terminal!")
            else:
                self.timer_hackeo -= dt
                if self.timer_hackeo <= 0:
                    self.shake.iniciar(8, 0.2)
                    audio.reproducir("explosion")
                    self.cortafuegos.remove(self.cortafuegos_actual)
                    self.hackeando = False
                    self.cortafuegos_rotos += 1
                    self.compañero.mostrar_mensaje(f"¡Roto! ({self.cortafuegos_rotos}/3) Alerta: Limpiador desplegado.")
                    self.monstruos.append(Monster(config.WIDTH - 100, config.HEIGHT - 100))

        for m in self.monstruos:
            if math.hypot(self.jugador.x - m.x, self.jugador.y - m.y) < (self.jugador.radio_nucleo + m.radio):
                self.startup() 
                self.shake.iniciar(15, 0.4)
                self.compañero.mostrar_mensaje("¡Te atrapó! Interviniendo código... Te devolví al inicio. ¡Corre!")
                break

        if self.salida.collidepoint(self.jugador.x, self.jugador.y):
            self.ganado = True
            if self.cortafuegos_rotos >= 3 and "L6" not in self.logros_obtenidos:
                save_manager.guardar(secreto="L6")
                self.compañero.mostrar_mensaje("¡LOGRO DESBLOQUEADO: Fuerza Bruta!")
                audio.reproducir("tecla")
            else:
                self.compañero.mostrar_mensaje("¡Laberinto superado! Volviendo al menú...")

    def dibujar(self, superficie):
        surf_temp = pygame.Surface((config.WIDTH, config.HEIGHT))
        surf_temp.fill((5, 5, 5))
        for p in self.paredes + self.paredes_falsas:
            pygame.draw.rect(surf_temp, (30, 30, 30), p)
            pygame.draw.rect(surf_temp, (50, 50, 50), p, 1) 
        for c in self.cortafuegos: pygame.draw.rect(surf_temp, config.COLOR_ENERGY, c) 
        pygame.draw.rect(surf_temp, (200, 200, 200), self.salida)
        
        if self.secreto_rect:
            pygame.draw.rect(surf_temp, config.COLOR_DANGER, self.secreto_rect)
            pygame.draw.rect(surf_temp, config.COLOR_TEXT, self.secreto_rect, 1)
        
        for m in self.monstruos: m.dibujar(surf_temp)
        self.jugador.dibujar(surf_temp)
        ox, oy = self.shake.obtener_offset()
        superficie.blit(surf_temp, (ox, oy))
        self.mascara.dibujar(superficie, (self.jugador.x, self.jugador.y))
        self.compañero.dibujar(superficie, self.jugador.y)