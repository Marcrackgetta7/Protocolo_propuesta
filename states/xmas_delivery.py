import pygame
import random
import math
from states.base_state import BaseState
from entities.player import Player
from utils.companion import CompanionUI
from utils import audio
from utils import save_manager
import config

class Casa:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 60, 60)
        self.entregado = False
    def dibujar(self, sup):
        color = (50, 200, 50) if self.entregado else (200, 50, 50)
        pygame.draw.rect(sup, color, self.rect)
        pygame.draw.rect(sup, (255, 255, 255), self.rect, 2)
        pygame.draw.polygon(sup, (100, 50, 20), [(self.rect.left, self.rect.top), (self.rect.centerx, self.rect.top-30), (self.rect.right, self.rect.top)])
        if self.entregado:
            rx, ry = self.rect.centerx - 10, self.rect.bottom - 20
            pygame.draw.rect(sup, (220, 20, 20), (rx, ry, 20, 20))
            pygame.draw.rect(sup, (255, 215, 0), (rx+8, ry, 4, 20)) 
            pygame.draw.rect(sup, (255, 215, 0), (rx, ry+8, 20, 4))

class XmasDelivery(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "OUTRO_3"
        self.jugador = None
        self.compañero = CompanionUI()
        self.casas = []
        self.entregas = 0
        self.tiempo = 15.0 
        self.ganado = False
        self.energia = 100.0 # Energía del trineo
        self.es_partida = True
        self.timer_victoria = 0.0

    def startup(self):
        self.jugador = Player(100, config.HEIGHT // 2)
        self.jugador.velocidad = 350 # Trineo rápido
        self.casas = []
        self.casas_entregadas = 0
        self.entregas = 0
        self.timer_fase = 0.0
        self.tiempo = 15.0
        self.energia = 100.0
        self.ganado = False
        self.timer_victoria = 0.0
        self.logros_obtenidos = save_manager.cargar().get("secretos", [])
        
        # Generar casas aleatorias sin que se solapen mucho
        for _ in range(5):
            x = random.randint(200, config.WIDTH - 100)
            y = random.randint(100, config.HEIGHT - 100)
            # Intentar separar las casas
            intentos = 0
            while intentos < 100:
                colision = False
                for casa in self.casas:
                    if math.hypot(casa["rect"].x - x, casa["rect"].y - y) < 140:
                        colision = True
                        break
                if not colision:
                    break
                x = random.randint(200, config.WIDTH - 100)
                y = random.randint(100, config.HEIGHT - 100)
                intentos += 1
                
            self.casas.append({"rect": pygame.Rect(x, y, 60, 60), "entregado": False})

        audio.reproducir_musica("assets/audio/fase3_nav.ogg", volumen=0.3)

    def manejar_eventos(self, evento):
        pass

    def actualizar(self, dt):
        self.compañero.actualizar(dt)
        self.timer_fase += dt
        
        if self.ganado:
            self.timer_victoria += dt
            if self.timer_victoria > 2.5:
                save_manager.guardar(fase=4) 
                self.done = True
            return

        self.tiempo -= dt
        if self.tiempo <= 0:
            audio.reproducir("explosion")
            self.startup() 
            return

        teclas = pygame.key.get_pressed()
        self.jugador.actualizar(dt, teclas)
        rect_jugador = pygame.Rect(self.jugador.x - 10, self.jugador.y - 10, 20, 20)

        for c in self.casas:
            if not c.entregado and rect_jugador.colliderect(c.rect):
                c.entregado = True
                self.entregas += 1
                audio.reproducir("anomalia")
                if self.entregas >= 5:
                    self.ganado = True
                    if self.tiempo >= 5.0 and "L3" not in self.logros_obtenidos:
                        save_manager.guardar(secreto="L3")
                        self.compañero.mostrar_mensaje(f"¡LOGRO DESBLOQUEADO: Santa Veloz! (+{self.tiempo:.1f}s sobrantes)")
                        audio.reproducir("tecla")
                    else:
                        self.compañero.mostrar_mensaje("¡Nivel Completado! Volviendo al menú...")

    def dibujar(self, superficie):
        superficie.fill((20, 40, 60))
        for c in self.casas: c.dibujar(superficie)
        self.jugador.dibujar(superficie)

        txt = pygame.font.SysFont("consolas", 24, bold=True).render(f"Tiempo: {max(0, self.tiempo):.1f}s | Entregas: {self.entregas}/5", True, (255, 50, 50) if self.tiempo < 5 else (255, 255, 255))
        superficie.blit(txt, (20, 20))
        self.compañero.dibujar(superficie, self.jugador.y)