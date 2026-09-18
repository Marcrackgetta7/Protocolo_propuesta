import pygame
import math
from states.base_state import BaseState
from entities.player import Player
from entities.monster import Monster
from utils.light_mask import LightMask
from utils.companion import CompanionUI
from utils.vfx import ScreenShake
from utils import audio
from utils import save_manager # <--- Importado aquí
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
    "1000000000001020000000E1",
    "111111111111111111111111",
]

class Maze(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "INTER_2" 
        self.tam_celda = 40 
        self.jugador = None
        self.monstruos = []
        self.mascara = LightMask()
        self.compañero = CompanionUI()
        self.shake = ScreenShake()
        self.paredes = []
        self.cortafuegos = []
        self.salida = None
        self.timer_hackeo = 0
        self.hackeando = False
        self.cortafuegos_actual = None

    def startup(self):
        self.paredes = []
        self.cortafuegos = []
        self.monstruos = []
        self.hackeando = False
        
        for fila in range(len(MAPA)):
            for col in range(len(MAPA[fila])):
                char = MAPA[fila][col]
                x = col * self.tam_celda
                y = fila * self.tam_celda
                rect = pygame.Rect(x, y, self.tam_celda, self.tam_celda)
                
                if char == "1": self.paredes.append(rect)
                elif char == "2": self.cortafuegos.append(rect)
                elif char == "S":
                    self.jugador = Player(x + self.tam_celda//2, y + self.tam_celda//2)
                    self.monstruos.append(Monster(config.WIDTH - 100, config.HEIGHT - 100))
                elif char == "E": self.salida = rect

        self.compañero.mostrar_mensaje("Archivos localizados. Corre a la salida, no dejes que el limpiador te toque.", id_voz="v_f2_in")

    def manejar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self.next_state = "MAIN_MENU"
            self.done = True

    def actualizar(self, dt):
        self.shake.actualizar(dt)
        self.compañero.actualizar(dt)
        teclas = pygame.key.get_pressed()
        vel = self.jugador.velocidad * dt
        
        dx = 0
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]: dx -= 1
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: dx += 1
        self.jugador.x += dx * vel
        rect_jugador = pygame.Rect(self.jugador.x - 10, self.jugador.y - 10, 20, 20)
        for p in self.paredes + self.cortafuegos:
            if rect_jugador.colliderect(p):
                self.jugador.x -= dx * vel 
                break

        dy = 0
        if teclas[pygame.K_UP] or teclas[pygame.K_w]: dy -= 1
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]: dy += 1
        self.jugador.y += dy * vel
        rect_jugador = pygame.Rect(self.jugador.x - 10, self.jugador.y - 10, 20, 20)
        for p in self.paredes + self.cortafuegos:
            if rect_jugador.colliderect(p):
                self.jugador.y -= dy * vel 
                break

        for m in self.monstruos: m.actualizar(dt, self.jugador.x, self.jugador.y)

        if not self.hackeando:
            for cf in self.cortafuegos:
                dist = math.hypot(self.jugador.x - (cf.x + 30), self.jugador.y - (cf.y + 30))
                if dist < 45:
                    self.hackeando = True
                    self.cortafuegos_actual = cf
                    self.timer_hackeo = 0.8 
                    self.compañero.mostrar_mensaje("¡Bloqueo! Dame un segundo, derribando cortafuegos...", id_voz="v_f2_hack")
                    break
        else:
            self.timer_hackeo -= dt
            if self.timer_hackeo <= 0:
                self.shake.iniciar(8, 0.2)
                audio.reproducir("explosion")
                self.cortafuegos.remove(self.cortafuegos_actual)
                self.hackeando = False
                self.compañero.mostrar_mensaje("¡Roto! Alerta: El sistema acaba de desplegar otro limpiador.", id_voz="v_f2_roto")
                self.monstruos.append(Monster(config.WIDTH - 100, config.HEIGHT - 100))

        for m in self.monstruos:
            dist_monstruo = math.hypot(self.jugador.x - m.x, self.jugador.y - m.y)
            if dist_monstruo < (self.jugador.radio_nucleo + m.radio):
                self.startup() 
                self.shake.iniciar(15, 0.4)
                self.compañero.mostrar_mensaje("¡Te atrapó! Interviniendo código... Te devolví al inicio. ¡Corre!", id_voz="v_f2_dead")
                break

        if self.salida.collidepoint(self.jugador.x, self.jugador.y):
            save_manager.guardar(3) # <--- GUARDA AL GANAR
            self.done = True

    def dibujar(self, superficie):
        surf_temp = pygame.Surface((config.WIDTH, config.HEIGHT))
        surf_temp.fill((5, 5, 5))
        for p in self.paredes:
            pygame.draw.rect(surf_temp, (30, 30, 30), p)
            pygame.draw.rect(surf_temp, (50, 50, 50), p, 1) 
        for c in self.cortafuegos: pygame.draw.rect(surf_temp, config.COLOR_ENERGY, c) 
        pygame.draw.rect(surf_temp, (200, 200, 200), self.salida)
        for m in self.monstruos: m.dibujar(surf_temp)
        self.jugador.dibujar(surf_temp)
        
        ox, oy = self.shake.obtener_offset()
        superficie.blit(surf_temp, (ox, oy))
        self.mascara.dibujar(superficie, (self.jugador.x, self.jugador.y))
        self.compañero.dibujar(superficie)