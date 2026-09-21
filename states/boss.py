import pygame
import math
import random
from states.base_state import BaseState
from entities.player import Player
from utils.companion import CompanionUI
from utils.vfx import ScreenShake
from utils import audio
from utils import save_manager 
import config

class BalaJugador:
    def __init__(self, x, y):
        self.x, self.y, self.vy, self.radio = x, y, -400, 4
    def actualizar(self, dt): self.y += self.vy * dt
    def dibujar(self, sup): pygame.draw.circle(sup, config.COLOR_TEXT, (int(self.x), int(self.y)), self.radio)

class ProyectilBoss:
    def __init__(self, x, y, tx, ty, speed=250):
        self.x, self.y = float(x), float(y)
        angulo = math.atan2(ty - y, tx - x)
        self.vx, self.vy = math.cos(angulo) * speed, math.sin(angulo) * speed
        self.radio = 6
    def actualizar(self, dt):
        self.x += self.vx * dt; self.y += self.vy * dt
    def dibujar(self, sup): pygame.draw.circle(sup, config.COLOR_ENERGY, (int(self.x), int(self.y)), self.radio)

class BarridoLaser:
    def __init__(self, speed, width):
        self.w, self.x, self.vx = width, -width, speed
    def actualizar(self, dt): self.x += self.vx * dt
    def dibujar(self, sup):
        surf = pygame.Surface((self.w, config.HEIGHT), pygame.SRCALPHA)
        surf.fill((255, 0, 0, 150)) 
        pygame.draw.rect(surf, (255, 255, 255), (self.w//2 - 5, 0, 10, config.HEIGHT)) 
        sup.blit(surf, (int(self.x), 0))

class Boss(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "CREDITS"
        self.jugador = None
        self.compañero = CompanionUI()
        self.shake = ScreenShake()
        
        self.proyectiles_boss, self.balas_jugador, self.barridos = [], [], []
        self.salud_jugador, self.escudo_jugador, self.salud_boss = 100, 100, 100
        self.timer_disparo_jugador, self.timer_fase, self.timer_disparo = 0.0, 0.0, 0.0
        self.timer_radial, self.timer_barrido = 0.0, 0.0
        self.hit_flash_timer = 0.0
        
        self.disparos_hechos = 0
        self.logro_pacifista_entregado = False
        
        self.estado = "INTRO"
        self.yo_x, self.yo_y = -100, -100
        self.es_partida = True
        self.fuente_ui = pygame.font.SysFont("consolas", 16, bold=True)

    def startup(self):
        self.jugador = Player(config.WIDTH / 2, config.HEIGHT - 100)
        self.proyectiles_boss, self.balas_jugador, self.barridos = [], [], []
        self.salud_jugador, self.escudo_jugador, self.salud_boss = 100, 100, 100
        self.estado = "INTRO"
        self.timer_fase, self.timer_disparo, self.timer_radial, self.timer_barrido = 0.0, 0.0, 0.0, 0.0
        self.disparos_hechos = 0
        self.hit_flash_timer = 0.0
        
        datos_guardados = save_manager.cargar()
        self.logro_pacifista_entregado = "Pacifista" in datos_guardados.get("secretos", [])
        
        self.yo_x, self.yo_y = -100, -100
        self.compañero.mostrar_mensaje("¡CUIDADO! Hemos despertado al Núcleo. ¡Dispara con ESPACIO!", id_voz="v_f3_in")
        audio.reproducir_musica("assets/audio/Jefe_dark.ogg", volumen=0.5)

    def manejar_eventos(self, evento): pass 

    def actualizar(self, dt):
        self.shake.actualizar(dt)
        self.compañero.actualizar(dt)
        teclas = pygame.key.get_pressed()
        factor_salud = max(0.01, self.salud_boss / 100.0)
        
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt
            
        if self.estado in ["INTRO", "COMBAT", "WARNING"]:
            self.jugador.actualizar(dt, teclas)
            if self.jugador.x < 20: self.jugador.x = 20
            if self.jugador.x > config.WIDTH - 20: self.jugador.x = config.WIDTH - 20
            if self.jugador.y < config.HEIGHT // 2 + 50: self.jugador.y = config.HEIGHT // 2 + 50
            if self.jugador.y > config.HEIGHT - 20: self.jugador.y = config.HEIGHT - 20
            
            # --- ARREGLO LOGRO PACIFISTA ---
            # El gatillo está 100% apagado durante la "INTRO". 
            # Puedes presionar espacio mil veces para leer que no disparará.
            if self.estado in ["COMBAT", "WARNING"]:
                self.timer_disparo_jugador -= dt
                if (teclas[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]) and self.timer_disparo_jugador <= 0:
                    self.balas_jugador.append(BalaJugador(self.jugador.x, self.jugador.y - 10))
                    self.timer_disparo_jugador = 0.15 
                    self.disparos_hechos += 1 
                    audio.reproducir("disparo_jugador", anti_spam_ms=100)
        
        self.timer_fase += dt

        if self.estado == "INTRO":
            if self.timer_fase > 3.0:
                self.estado = "COMBAT"
                self.timer_fase = 0.0
                self.compañero.mostrar_mensaje("¡Trata de bajarle la vida! Te protegeré con los escudos.", id_voz="v_f3_esc")

        elif self.estado == "COMBAT":
            if self.timer_fase > 15.0 and self.disparos_hechos == 0 and not self.logro_pacifista_entregado:
                save_manager.guardar(secreto="Pacifista")
                self.logro_pacifista_entregado = True
                self.compañero.mostrar_mensaje("¡LOGRO DESBLOQUEADO: Pacifista (15s sin disparar)!")
                audio.reproducir("tecla")

            self.timer_disparo += dt
            self.timer_radial += dt
            self.timer_barrido += dt
            
            if self.timer_barrido > 3.0 + (5.0 * factor_salud):
                vel_barrido = 250 + (400 * (1.0 - factor_salud))
                ancho_barrido = 60 + (60 * (1.0 - factor_salud))
                self.barridos.append(BarridoLaser(vel_barrido, ancho_barrido))
                self.timer_barrido = 0.0
                audio.reproducir("laser_final")
                self.shake.iniciar(8, 0.5)

            if self.timer_disparo > 0.02 + (0.15 * factor_salud): 
                tx, ty = self.jugador.x + random.randint(-40, 40), self.jugador.y
                vel_bala = 350 + (200 * (1.0 - factor_salud)) 
                self.proyectiles_boss.append(ProyectilBoss(self.boss_x, self.boss_y, tx, ty, speed=vel_bala))
                self.timer_disparo = 0.0
                audio.reproducir("disparo_boss", anti_spam_ms=60)

            if self.timer_radial > 0.3 + (1.2 * factor_salud):
                self.shake.iniciar(5, 0.2)
                audio.reproducir("boss_area", anti_spam_ms=300)
                for i in range(16): 
                    angulo = i * (math.pi / 8)
                    tx, ty = self.boss_x + math.cos(angulo) * 100, self.boss_y + math.sin(angulo) * 100
                    vel_radial = 200 + (100 * (1.0 - factor_salud))
                    self.proyectiles_boss.append(ProyectilBoss(self.boss_x, self.boss_y, tx, ty, speed=vel_radial))
                self.timer_radial = 0.0

            if self.salud_jugador <= 20 or self.salud_boss <= 1:
                self.estado = "WARNING"
                self.timer_fase = 0.0
                audio.reproducir("laser_final")
                if self.salud_boss <= 1: self.compañero.mostrar_mensaje("¡Lo logramos! Espera... ¡Núcleo crítico! ¡Va a autodestruirse con el láser!", id_voz="v_f3_win")
                else: self.compañero.mostrar_mensaje("¡ALERTA! Va a usar el láser de purga... ¡Tus escudos no resistirán!", id_voz="v_f3_alert")
                self.shake.iniciar(8, 2.0)

        elif self.estado == "WARNING":
            if self.timer_fase > 3.0:
                self.estado = "SACRIFICE"
                self.timer_fase = 0.0
                self.yo_x, self.yo_y = self.jugador.x, self.jugador.y - 50 
                self.shake.iniciar(25, 4.0)
                self.compañero.mostrar_mensaje("¡Escudos críticos! No vas a sobrevivir a eso...", id_voz="v_f3_crit")

        elif self.estado == "SACRIFICE":
            if 1.5 < self.timer_fase < 1.6: self.compañero.mostrar_mensaje("Redirigiendo todo el impacto hacia mi terminal...", id_voz="v_f3_sac1")
            elif 3.5 < self.timer_fase < 3.6: self.compañero.mostrar_mensaje("Sobrecarga inminente. ¡Forzando apagado de emergencia del sistema!", id_voz="v_f3_sac2")
            if self.timer_fase > 5.5:
                self.estado = "GLITCH"
                self.timer_fase = 0.0
                self.shake.iniciar(40, 2.0)
                audio.reproducir("glitch", parar_anterior=True)
                audio.detener_musica()

        elif self.estado == "GLITCH":
            if self.timer_fase > 2.0:
                audio.detener_sonido("glitch") 
                self.done = True 

        for b in self.balas_jugador[:]:
            b.actualizar(dt)
            if b.y < 0: self.balas_jugador.remove(b)
            elif math.hypot(self.boss_x - b.x, self.boss_y - b.y) < 50:
                self.hit_flash_timer = 0.1
                if b in self.balas_jugador: self.balas_jugador.remove(b)
                if self.salud_boss > 1: self.salud_boss -= 1

        for p in self.proyectiles_boss[:]:
            p.actualizar(dt)
            if p.y > config.HEIGHT or p.x < 0 or p.x > config.WIDTH: self.proyectiles_boss.remove(p)
            elif self.estado in ["INTRO", "COMBAT"]:
                if math.hypot(self.jugador.x - p.x, self.jugador.y - p.y) < self.jugador.radio_nucleo + p.radio:
                    self.shake.iniciar(10, 0.2)
                    self.proyectiles_boss.remove(p)
                    if self.escudo_jugador > 0: self.escudo_jugador -= 10
                    else: self.salud_jugador -= 10
                    
        for barrido in self.barridos[:]:
            barrido.actualizar(dt)
            if barrido.x > config.WIDTH: self.barridos.remove(barrido)
            elif self.estado == "COMBAT":
                if barrido.x < self.jugador.x < barrido.x + barrido.w:
                    self.shake.iniciar(10, 0.1)
                    if self.escudo_jugador > 0: self.escudo_jugador -= 30 * dt
                    else: self.salud_jugador -= 30 * dt

    def dibujar(self, superficie):
        surf_temp = pygame.Surface((config.WIDTH, config.HEIGHT))
        surf_temp.fill(config.COLOR_BG)
        for b in self.balas_jugador: b.dibujar(surf_temp)
        self.jugador.dibujar(surf_temp)

        if self.estado in ["SACRIFICE", "GLITCH"]:
            pygame.draw.circle(surf_temp, (0, 255, 100), (int(self.yo_x), int(self.yo_y)), 10)
            pygame.draw.circle(surf_temp, (0, 255, 100, 100), (int(self.yo_x), int(self.yo_y)), min(150, 60 + int(self.timer_fase * 20)), 3) 

        color_ext = (255, 255, 255) if self.hit_flash_timer > 0 else (100, 0, 0)
        color_int = (255, 255, 255) if self.hit_flash_timer > 0 else config.COLOR_DANGER
        pygame.draw.circle(surf_temp, color_ext, (int(self.boss_x), int(self.boss_y)), 50)
        pygame.draw.circle(surf_temp, color_int, (int(self.boss_x), int(self.boss_y)), 25)

        surf_temp.blit(self.fuente_ui.render(f"SALUD: {max(0, int(self.salud_jugador))}%", True, config.COLOR_TEXT), (20, 20))
        surf_temp.blit(self.fuente_ui.render(f"ESCUDO: {max(0, int(self.escudo_jugador))}%", True, (0, 200, 255)), (20, 45))
        surf_temp.blit(self.fuente_ui.render(f"NÚCLEO: {max(1, int(self.salud_boss))}%", True, config.COLOR_DANGER), (config.WIDTH - 150, 20))
        pygame.draw.rect(surf_temp, (50, 0, 0), (config.WIDTH - 150, 45, 120, 10))
        pygame.draw.rect(surf_temp, config.COLOR_DANGER, (config.WIDTH - 150, 45, 120 * (self.salud_boss/100.0), 10))

        if self.estado == "WARNING":
            pygame.draw.rect(surf_temp, (200, 200, 200), (self.jugador.x - 40, self.boss_y, 80, config.HEIGHT), 2)
        elif self.estado == "SACRIFICE":
            pygame.draw.rect(surf_temp, config.COLOR_DANGER, (self.jugador.x - 40, self.boss_y, 80, self.yo_y - self.boss_y)) 
            pygame.draw.circle(surf_temp, (255, 255, 255), (int(self.yo_x), int(self.yo_y)), random.randint(50, 90)) 
        elif self.estado == "GLITCH":
            for _ in range(30):
                rx, ry, rw, rh = random.randint(0, config.WIDTH), random.randint(0, config.HEIGHT), random.randint(10, 300), random.randint(5, 80)
                pygame.draw.rect(surf_temp, random.choice([config.COLOR_DANGER, (0, 255, 100), (200, 200, 200)]), (rx, ry, rw, rh))

        for p in self.proyectiles_boss: p.dibujar(surf_temp)
        for barrido in self.barridos: barrido.dibujar(surf_temp)
        
        ox, oy = self.shake.obtener_offset()
        superficie.blit(surf_temp, (ox, oy))
        
        if self.estado != "GLITCH": 
            self.compañero.dibujar(superficie, self.jugador.y)