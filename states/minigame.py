import pygame
import random
import math
from states.base_state import BaseState
from entities.player import Player
from entities.anomaly import Anomaly
from entities.laser import Laser
from utils.vfx import ScreenShake
from utils.companion import CompanionUI
from utils import audio
from utils import save_manager
import config

class Minigame(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "OUTRO_5" 
        self.jugador = None
        self.anomalias = []
        self.anomalias_recolectadas = 0
        self.lasers = []
        self.timer_laser = 0.0
        self.shake = ScreenShake()
        self.compañero = CompanionUI()
        self.es_partida = True
        
        self.golpes_laser = 0
        self.ganado = False
        self.timer_victoria = 0.0

    def startup(self):
        self.jugador = Player(config.WIDTH / 2, config.HEIGHT / 2)
        self.anomalias, self.lasers = [], []
        self.anomalias_recolectadas, self.timer_laser = 0, 0.0
        self.golpes_laser, self.ganado, self.timer_victoria = 0, False, 0.0
        self.logros_obtenidos = save_manager.cargar().get("secretos", [])
        
        self.spawn_anomalia()
        self.compañero.mostrar_mensaje("Infiltración detectada. Muévete rápido, te cubro las espaldas.", id_voz="v_f1_in")
        audio.reproducir_musica("assets/audio/Fase1_dark.ogg", volumen=0.4)

    def spawn_anomalia(self):
        distancia = 0
        x, y = 0, 0
        while distancia < 250:
            x, y = random.randint(50, config.WIDTH - 50), random.randint(50, config.HEIGHT - 50) 
            if not self.jugador: break
            distancia = math.hypot(self.jugador.x - x, self.jugador.y - y)
        self.anomalias.append(Anomaly(x, y))

    def spawn_laser(self):
        es_horizontal = random.choice([True, False])
        pos = random.randint(50, config.HEIGHT - 50) if es_horizontal else random.randint(50, config.WIDTH - 50)
        l = Laser(es_horizontal, pos)
        factor = self.anomalias_recolectadas * 0.1
        l.tiempo_aviso = max(0.25, 0.6 - factor)
        l.tiempo_activo = max(0.15, 0.3 - factor/2)
        self.lasers.append(l)
        audio.reproducir("laser_fase1", anti_spam_ms=100)

    def manejar_eventos(self, evento):
        pass

    def actualizar(self, dt):
        self.shake.actualizar(dt)
        self.compañero.actualizar(dt)
        
        if self.ganado:
            self.timer_victoria += dt
            if self.timer_victoria > 1.5:
                save_manager.guardar(fase=6)
                self.done = True
            return

        teclas = pygame.key.get_pressed()
        self.jugador.actualizar(dt, teclas)
        
        if self.jugador.x < 20: self.jugador.x = 20
        if self.jugador.x > config.WIDTH - 20: self.jugador.x = config.WIDTH - 20
        if self.jugador.y < 20: self.jugador.y = 20
        if self.jugador.y > config.HEIGHT - 20: self.jugador.y = config.HEIGHT - 20

        intervalo_laser = max(0.2, 0.8 - (self.anomalias_recolectadas * 0.15))
        self.timer_laser += dt
        if self.timer_laser >= intervalo_laser: 
            self.spawn_laser()
            if self.anomalias_recolectadas >= 2 and random.random() < 0.4: self.spawn_laser() 
            elif self.anomalias_recolectadas >= 4:
                self.spawn_laser() 
                if random.random() < 0.5: self.spawn_laser() 
            self.timer_laser = 0.0

        for laser in self.lasers[:]:
            laser.actualizar(dt)
            if laser.terminado: self.lasers.remove(laser)
            elif laser.estado == "ACTIVO" and laser.rect.collidepoint(self.jugador.x, self.jugador.y):
                self.jugador.x, self.jugador.y = config.WIDTH / 2, config.HEIGHT / 2
                self.shake.iniciar(intensidad=12, duracion=0.3)
                self.golpes_laser += 1

        for anomalia in self.anomalias[:]:
            anomalia.actualizar(dt)
            if not anomalia.recolectada:
                dist = math.hypot(self.jugador.x - anomalia.x, self.jugador.y - anomalia.y)
                if dist < (self.jugador.radio_nucleo + anomalia.radio):
                    anomalia.recolectada = True
                    self.anomalias_recolectadas += 1
                    audio.reproducir("anomalia")
                    
                    if self.anomalias_recolectadas == 2: self.compañero.mostrar_mensaje("¡Bien! Cuidado, el sistema está acelerando...", id_voz="v_f1_mid")
                    elif self.anomalias_recolectadas == 4: self.compañero.mostrar_mensaje("¡Solo falta una! ¡Cuidado con el ataque múltiple!", id_voz="v_f1_fin")
                    if self.anomalias_recolectadas < 5: self.spawn_anomalia()
                    else: 
                        self.ganado = True
                        if self.golpes_laser == 0 and "L5" not in self.logros_obtenidos:
                            save_manager.guardar(secreto="L5")
                            self.compañero.mostrar_mensaje("¡LOGRO DESBLOQUEADO: Fantasma Digital (Cero Láseres)!")
                            audio.reproducir("tecla")
                        else:
                            self.compañero.mostrar_mensaje("¡Infiltración completada! Extrayendo...")

    def dibujar(self, superficie):
        surf_temp = pygame.Surface((config.WIDTH, config.HEIGHT))
        surf_temp.fill(config.COLOR_BG)
        color_linea = (20, 20, 20)
        for x in range(0, config.WIDTH, 40): pygame.draw.line(surf_temp, color_linea, (x, 0), (x, config.HEIGHT))
        for y in range(0, config.HEIGHT, 40): pygame.draw.line(surf_temp, color_linea, (0, y), (config.WIDTH, y))
        
        for laser in self.lasers: laser.dibujar(surf_temp)
        for anomalia in self.anomalias: anomalia.dibujar(surf_temp)
        self.jugador.dibujar(surf_temp)
        
        # Add UI counter
        font = pygame.font.SysFont("consolas", 24, bold=True)
        txt = font.render(f"Anomalías: {self.anomalias_recolectadas}/5", True, config.COLOR_ENERGY)
        surf_temp.blit(txt, (20, 20))
        
        ox, oy = self.shake.obtener_offset()
        superficie.blit(surf_temp, (ox, oy))
        self.compañero.dibujar(superficie, self.jugador.y)