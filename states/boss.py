import pygame
import math
import random
from states.base_state import BaseState
from entities.player import Player
from utils.companion import CompanionUI
from utils.vfx import ScreenShake
from utils import audio
import config

class BalaJugador:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vy = -400 
        self.radio = 4
    def actualizar(self, dt): self.y += self.vy * dt
    def dibujar(self, sup): pygame.draw.circle(sup, config.COLOR_TEXT, (int(self.x), int(self.y)), self.radio)

class ProyectilBoss:
    def __init__(self, x, y, tx, ty, speed=250):
        self.x = float(x)
        self.y = float(y)
        angulo = math.atan2(ty - y, tx - x)
        self.vx = math.cos(angulo) * speed
        self.vy = math.sin(angulo) * speed
        self.radio = 6
    def actualizar(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
    def dibujar(self, sup): pygame.draw.circle(sup, config.COLOR_ENERGY, (int(self.x), int(self.y)), self.radio)

class Boss(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "CREDITS"
        self.jugador = None
        self.compañero = CompanionUI()
        self.shake = ScreenShake()
        self.proyectiles_boss = []
        self.balas_jugador = []
        
        self.salud_jugador = 100
        self.escudo_jugador = 100
        self.salud_boss = 100
        self.timer_disparo_jugador = 0.0
        
        self.timer_fase = 0.0
        self.timer_disparo = 0.0
        self.timer_radial = 0.0
        self.estado = "INTRO"
        self.boss_x = config.WIDTH / 2
        self.boss_y = 100
        self.yo_x = -100
        self.yo_y = -100

    def startup(self):
        self.jugador = Player(config.WIDTH / 2, config.HEIGHT - 100)
        self.proyectiles_boss = []
        self.balas_jugador = []
        self.salud_jugador = 100
        self.escudo_jugador = 100
        self.salud_boss = 100
        self.estado = "INTRO"
        self.timer_fase = 0.0
        self.timer_disparo = 0.0
        self.timer_radial = 0.0
        self.yo_x = -100
        self.yo_y = -100
        self.compañero.mostrar_mensaje("¡CUIDADO! Hemos despertado al Núcleo. ¡Dispara con ESPACIO!")
        
        audio.reproducir_musica("assets/audio/bgm_boss.ogg", volumen=0.5)

    def manejar_eventos(self, evento):
        pass 

    def actualizar(self, dt):
        self.shake.actualizar(dt)
        self.compañero.actualizar(dt)
        teclas = pygame.key.get_pressed()
        
        if self.estado in ["INTRO", "COMBAT", "WARNING"]:
            self.jugador.actualizar(dt, teclas)
            
            self.timer_disparo_jugador -= dt
            if (teclas[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]) and self.timer_disparo_jugador <= 0:
                self.balas_jugador.append(BalaJugador(self.jugador.x, self.jugador.y - 10))
                self.timer_disparo_jugador = 0.15 
                audio.reproducir("disparo_jugador", anti_spam_ms=100)
        
        self.timer_fase += dt

        if self.estado == "INTRO":
            if self.timer_fase > 3.0:
                self.estado = "COMBAT"
                self.timer_fase = 0.0
                self.compañero.mostrar_mensaje("¡Trata de bajarle la vida! Te protegeré con los escudos.")

        elif self.estado == "COMBAT":
            self.timer_disparo += dt
            self.timer_radial += dt
            
            factor_salud = max(0.2, self.salud_boss / 100.0)
            intervalo_dirigido = 0.04 + (0.11 * factor_salud) 
            intervalo_radial = 0.5 + (1.0 * factor_salud)     
            
            if self.timer_disparo > intervalo_dirigido: 
                tx = self.jugador.x + random.randint(-20, 20)
                ty = self.jugador.y
                vel_bala = 350 + (100 * (1.0 - factor_salud)) 
                self.proyectiles_boss.append(ProyectilBoss(self.boss_x, self.boss_y, tx, ty, speed=vel_bala))
                self.timer_disparo = 0.0
                audio.reproducir("disparo_boss", anti_spam_ms=60)

            if self.timer_radial > intervalo_radial:
                self.shake.iniciar(5, 0.2)
                audio.reproducir("boss_area", anti_spam_ms=300)
                for i in range(16): 
                    angulo = i * (math.pi / 8)
                    tx = self.boss_x + math.cos(angulo) * 100
                    ty = self.boss_y + math.sin(angulo) * 100
                    vel_radial = 200 + (50 * (1.0 - factor_salud))
                    self.proyectiles_boss.append(ProyectilBoss(self.boss_x, self.boss_y, tx, ty, speed=vel_radial))
                self.timer_radial = 0.0

            if self.salud_jugador <= 20 or self.salud_boss <= 1:
                self.estado = "WARNING"
                self.timer_fase = 0.0
                audio.reproducir("laser_final")
                
                if self.salud_boss <= 1:
                    self.compañero.mostrar_mensaje("¡Lo logramos! Espera... ¡Núcleo crítico! ¡Va a autodestruirse con el láser!")
                else:
                    self.compañero.mostrar_mensaje("¡ALERTA! Va a usar el láser de purga... ¡Tus escudos no resistirán!")
                    
                self.shake.iniciar(8, 2.0)

        elif self.estado == "WARNING":
            if self.timer_fase > 3.0:
                self.estado = "SACRIFICE"
                self.timer_fase = 0.0
                self.yo_x = self.jugador.x
                self.yo_y = self.jugador.y - 50 
                self.shake.iniciar(25, 4.0)
                self.compañero.mostrar_mensaje("¡Escudos críticos! No vas a sobrevivir a eso...")

        elif self.estado == "SACRIFICE":
            if self.timer_fase > 1.5 and self.timer_fase < 1.6:
                self.compañero.mostrar_mensaje("Redirigiendo todo el impacto hacia mi terminal...")
            elif self.timer_fase > 3.5 and self.timer_fase < 3.6:
                self.compañero.mostrar_mensaje("Sobrecarga inminente. ¡Forzando apagado de emergencia del sistema!")
                
            if self.timer_fase > 5.5:
                self.estado = "GLITCH"
                self.timer_fase = 0.0
                self.shake.iniciar(40, 2.0)
                audio.reproducir("glitch") 
                audio.detener_musica()

        elif self.estado == "GLITCH":
            if self.timer_fase > 2.0:
                # ¡CORRECCIÓN! Callamos el ruido a la fuerza antes de cambiar a los créditos
                audio.detener_sonido("glitch") 
                self.done = True 

        for b in self.balas_jugador[:]:
            b.actualizar(dt)
            if b.y < 0:
                self.balas_jugador.remove(b)
            elif math.hypot(self.boss_x - b.x, self.boss_y - b.y) < 50:
                if b in self.balas_jugador: self.balas_jugador.remove(b)
                if self.salud_boss > 1:
                    self.salud_boss -= 1

        for p in self.proyectiles_boss[:]:
            p.actualizar(dt)
            if p.y > config.HEIGHT or p.x < 0 or p.x > config.WIDTH:
                self.proyectiles_boss.remove(p)
            elif self.estado in ["INTRO", "COMBAT"]:
                if math.hypot(self.jugador.x - p.x, self.jugador.y - p.y) < self.jugador.radio_nucleo + p.radio:
                    self.shake.iniciar(10, 0.2)
                    self.proyectiles_boss.remove(p)
                    if self.escudo_jugador > 0:
                        self.escudo_jugador -= 10
                    else:
                        self.salud_jugador -= 10

    def dibujar(self, superficie):
        surf_temp = pygame.Surface((config.WIDTH, config.HEIGHT))
        surf_temp.fill(config.COLOR_BG)

        for b in self.balas_jugador:
            b.dibujar(surf_temp)

        self.jugador.dibujar(surf_temp)

        if self.estado in ["SACRIFICE", "GLITCH"]:
            pygame.draw.circle(surf_temp, (0, 255, 100), (int(self.yo_x), int(self.yo_y)), 10)
            radio_aura = min(150, 60 + int(self.timer_fase * 20))
            pygame.draw.circle(surf_temp, (0, 255, 100, 100), (int(self.yo_x), int(self.yo_y)), radio_aura, 3) 

        pygame.draw.circle(surf_temp, (100, 0, 0), (int(self.boss_x), int(self.boss_y)), 50)
        pygame.draw.circle(surf_temp, config.COLOR_DANGER, (int(self.boss_x), int(self.boss_y)), 25)

        fuente_ui = pygame.font.SysFont("consolas", 16, bold=True)
        txt_salud = fuente_ui.render(f"SALUD: {max(0, self.salud_jugador)}%", True, config.COLOR_TEXT)
        txt_escudo = fuente_ui.render(f"ESCUDO: {max(0, self.escudo_jugador)}%", True, (0, 200, 255))
        surf_temp.blit(txt_salud, (20, 20))
        surf_temp.blit(txt_escudo, (20, 45))
        
        txt_boss = fuente_ui.render(f"NÚCLEO: {max(1, self.salud_boss)}%", True, config.COLOR_DANGER)
        surf_temp.blit(txt_boss, (config.WIDTH - 150, 20))
        pygame.draw.rect(surf_temp, (50, 0, 0), (config.WIDTH - 150, 45, 120, 10))
        pygame.draw.rect(surf_temp, config.COLOR_DANGER, (config.WIDTH - 150, 45, 120 * (self.salud_boss/100.0), 10))

        if self.estado == "WARNING":
            pygame.draw.rect(surf_temp, (200, 200, 200), (self.jugador.x - 40, self.boss_y, 80, config.HEIGHT), 2)
        elif self.estado == "SACRIFICE":
            pygame.draw.rect(surf_temp, config.COLOR_DANGER, (self.jugador.x - 40, self.boss_y, 80, self.yo_y - self.boss_y)) 
            pygame.draw.circle(surf_temp, (255, 255, 255), (int(self.yo_x), int(self.yo_y)), random.randint(50, 90)) 

        elif self.estado == "GLITCH":
            for _ in range(30):
                rx = random.randint(0, config.WIDTH)
                ry = random.randint(0, config.HEIGHT)
                rw = random.randint(10, 300)
                rh = random.randint(5, 80)
                pygame.draw.rect(surf_temp, random.choice([config.COLOR_DANGER, (0, 255, 100), (200, 200, 200)]), (rx, ry, rw, rh))

        for p in self.proyectiles_boss:
            p.dibujar(surf_temp)

        ox, oy = self.shake.obtener_offset()
        superficie.blit(surf_temp, (ox, oy))
        
        if self.estado != "GLITCH":
            self.compañero.dibujar(superficie)