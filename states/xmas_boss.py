import pygame
import math
import random
from states.base_state import BaseState
from entities.player import Player
from utils.companion import CompanionUI
from utils import audio
from utils import save_manager
import config

class BolaNieve:
    def __init__(self, x, y, vx, vy):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
    def actualizar(self, dt):
        self.x += self.vx * dt; self.y += self.vy * dt
    def dibujar(self, sup): pygame.draw.circle(sup, (220, 240, 255), (int(self.x), int(self.y)), 8)

class RegaloBala:
    def __init__(self, x, y):
        self.x, self.y, self.vy = x, y, -350
    def actualizar(self, dt): self.y += self.vy * dt
    def dibujar(self, sup):
        pygame.draw.rect(sup, (220, 20, 20), (int(self.x)-6, int(self.y)-6, 12, 12))
        pygame.draw.rect(sup, (255, 215, 0), (int(self.x)-2, int(self.y)-6, 4, 12))

class ZonaCalor:
    def __init__(self, x, y):
        self.x, self.y, self.radio, self.timer = x, y, 60, 6.0 
    def actualizar(self, dt): self.timer -= dt
    def dibujar(self, sup):
        pygame.draw.circle(sup, (255, 100, 0, 80), (int(self.x), int(self.y)), self.radio)
        pygame.draw.circle(sup, (255, 150, 0), (int(self.x), int(self.y)), 10)
        pygame.draw.circle(sup, (255, 50, 0), (int(self.x), int(self.y)), self.radio, 2)

class XmasBoss(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "OUTRO_4"
        self.jugador = None
        self.compañero = CompanionUI()
        self.bolas, self.mis_balas, self.zonas_calor = [], [], []
        self.salud_boss, self.congelacion, self.congelado = 100, 0.0, False
        self.timer_descongelar, self.vel_original = 0.0, 300
        self.boss_x, self.boss_y = config.WIDTH / 2, 100
        self.timer_disparo, self.timer_aoe, self.timer_ayuda, self.timer_bala_jugador = 0.0, 0.0, 0.0, 0.0
        
        self.se_congelo_alguna_vez = False
        self.ganado = False
        self.timer_victoria = 0.0
        self.es_partida = True
    def startup(self):
        self.jugador = Player(config.WIDTH / 2, config.HEIGHT - 150)
        self.vel_original = self.jugador.velocidad 
        self.bolas, self.mis_balas, self.zonas_calor = [], [], []
        self.salud_boss, self.congelacion, self.congelado = 100, 0.0, False
        self.se_congelo_alguna_vez, self.ganado, self.timer_victoria = False, False, 0.0
        self.logros_obtenidos = save_manager.cargar().get("secretos", [])
        
        self.compañero.mostrar_mensaje("¡Cuidado con la nieve! Mientras más te enfríes, más lento te moverás y dispararás.")
        audio.reproducir_musica("assets/audio/Jefe_nav.ogg", volumen=0.5)

    def manejar_eventos(self, evento):
        pass

    def actualizar(self, dt):
        self.compañero.actualizar(dt)
        
        if self.ganado:
            self.timer_victoria += dt
            if self.timer_victoria > 3.0:
                save_manager.guardar(fase=5) 
                self.done = True
            return

        teclas = pygame.key.get_pressed()
        factor_salud = max(0.1, self.salud_boss / 100.0)

        if self.congelado:
            self.timer_descongelar -= dt
            self.salud_boss = min(100, self.salud_boss + (15 * dt)) 
            if self.timer_descongelar <= 0:
                self.congelado, self.congelacion = False, 0.0
        else:
            factor_frio = self.congelacion / 100.0 
            self.jugador.velocidad = self.vel_original * max(0.2, 1.0 - factor_frio)
            self.jugador.actualizar(dt, teclas)
            self.congelacion = max(0, self.congelacion - (2 * dt)) 
            
            self.timer_bala_jugador -= dt
            if teclas[pygame.K_SPACE] and self.timer_bala_jugador <= 0:
                self.mis_balas.append(RegaloBala(self.jugador.x, self.jugador.y))
                self.timer_bala_jugador = 0.2 + (0.8 * factor_frio)
                audio.reproducir("anomalia", anti_spam_ms=100)

        if self.jugador.x < 20: self.jugador.x = 20
        if self.jugador.x > config.WIDTH - 20: self.jugador.x = config.WIDTH - 20
        if self.jugador.y < config.HEIGHT // 2 + 50: self.jugador.y = config.HEIGHT // 2 + 50
        if self.jugador.y > config.HEIGHT - 20: self.jugador.y = config.HEIGHT - 20

        self.timer_ayuda += dt
        if self.timer_ayuda > 8.0: 
            self.zonas_calor.append(ZonaCalor(random.randint(100, config.WIDTH-100), random.randint(config.HEIGHT//2+50, config.HEIGHT-50)))
            self.timer_ayuda = 0.0
            self.compañero.mostrar_mensaje("¡Te envié un núcleo de calor! Quédate ahí para descongelarte.")

        for z in self.zonas_calor[:]:
            z.actualizar(dt)
            if z.timer <= 0: self.zonas_calor.remove(z)
            elif math.hypot(self.jugador.x - z.x, self.jugador.y - z.y) < z.radio:
                self.congelacion = max(0, self.congelacion - (40 * dt)) 

        self.boss_x = (config.WIDTH / 2) + math.sin(pygame.time.get_ticks() * 0.002) * 200

        self.timer_disparo += dt
        if self.timer_disparo > 0.1 + (0.4 * factor_salud):
            self.bolas.append(BolaNieve(self.boss_x, self.boss_y + 30, random.randint(-100, 100), 200 + (100 * (1-factor_salud))))
            self.timer_disparo = 0.0

        self.timer_aoe += dt
        if self.timer_aoe > 1.5 + (3.0 * factor_salud):
            for i in range(12):
                ang = i * (math.pi / 6)
                self.bolas.append(BolaNieve(self.boss_x, self.boss_y+30, math.cos(ang)*200, math.sin(ang)*200))
            self.timer_aoe = 0.0
            audio.reproducir("boss_area", anti_spam_ms=300)

        for b in self.mis_balas[:]:
            b.actualizar(dt)
            if b.y < 0: self.mis_balas.remove(b)
            elif math.hypot(self.boss_x - b.x, self.boss_y - b.y) < 40:
                self.salud_boss -= 2
                if b in self.mis_balas: self.mis_balas.remove(b)

        for b in self.bolas[:]:
            b.actualizar(dt)
            if b.y > config.HEIGHT or b.x < 0 or b.x > config.WIDTH: self.bolas.remove(b)
            elif not self.congelado and math.hypot(self.jugador.x - b.x, self.jugador.y - b.y) < 15:
                self.congelacion += 15 
                if b in self.bolas: self.bolas.remove(b)
                if self.congelacion >= 100:
                    self.congelacion = 100
                    self.congelado, self.se_congelo_alguna_vez = True, True
                    self.timer_descongelar = 3.0
                    self.compañero.mostrar_mensaje("¡TE HAS CONGELADO! No puedes moverte y el jefe se está curando.")
                    audio.reproducir("explosion")

        if self.salud_boss <= 0 and not self.ganado:
            self.ganado = True
            if not self.se_congelo_alguna_vez and "L4" not in self.logros_obtenidos:
                save_manager.guardar(secreto="L4")
                self.compañero.mostrar_mensaje("¡LOGRO DESBLOQUEADO: Sangre Caliente (Cero congelaciones)!")
                audio.reproducir("tecla")
            else:
                self.compañero.mostrar_mensaje("¡Muñeco de nieve destruido! Volviendo al menú...")

    def dibujar(self, superficie):
        superficie.fill((20, 40, 60))
        surf_alpha = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        for z in self.zonas_calor: z.dibujar(surf_alpha)
        superficie.blit(surf_alpha, (0,0))
        for b in self.mis_balas + self.bolas: b.dibujar(superficie)
        
        if self.congelado: pygame.draw.rect(superficie, (150, 200, 255), (self.jugador.x-15, self.jugador.y-15, 30, 30)) 
        self.jugador.dibujar(superficie)
        pygame.draw.circle(superficie, (255, 255, 255), (int(self.boss_x), int(self.boss_y)), 30)
        pygame.draw.circle(superficie, (255, 255, 255), (int(self.boss_x), int(self.boss_y) - 40), 20)
        
        pygame.draw.rect(superficie, (50, 255, 50), (config.WIDTH//2 - 100, 20, 200, 15))
        pygame.draw.rect(superficie, (255, 50, 50), (config.WIDTH//2 - 100, 20, max(0, self.salud_boss)*2, 15))
        
        fuente = pygame.font.SysFont("consolas", 14, bold=True)
        superficie.blit(fuente.render("FRÍO:", True, (150, 200, 255)), (20, 20))
        pygame.draw.rect(superficie, (30, 60, 100), (70, 20, 100, 15))
        pygame.draw.rect(superficie, (0, 150, 255), (70, 20, self.congelacion, 15))
        self.compañero.dibujar(superficie, self.jugador.y)