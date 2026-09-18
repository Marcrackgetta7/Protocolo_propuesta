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
from utils import save_manager # <--- Importado aquí
import config

class Minigame(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "INTER_1" 
        self.jugador = None
        self.anomalias = []
        self.anomalias_recolectadas = 0
        self.lasers = []
        self.timer_laser = 0.0
        self.shake = ScreenShake()
        self.compañero = CompanionUI()

    def startup(self):
        self.jugador = Player(config.WIDTH / 2, config.HEIGHT / 2)
        self.anomalias = []
        self.lasers = []
        self.anomalias_recolectadas = 0
        self.timer_laser = 0.0
        self.spawn_anomalia()
        self.compañero.mostrar_mensaje("Infiltración detectada. Muévete rápido, te cubro las espaldas.", id_voz="v_f1_in")
        audio.reproducir_musica("assets/audio/bgm_misterio.ogg", volumen=0.4)

    def spawn_anomalia(self):
        distancia = 0
        x, y = 0, 0
        while distancia < 250:
            x = random.randint(50, config.WIDTH - 50)
            y = random.randint(50, config.HEIGHT - 100)
            if not self.jugador: 
                break
            distancia = math.hypot(self.jugador.x - x, self.jugador.y - y)
        self.anomalias.append(Anomaly(x, y))

    def spawn_laser(self):
        es_horizontal = random.choice([True, False])
        if es_horizontal: pos = random.randint(50, config.HEIGHT - 100)
        else: pos = random.randint(50, config.WIDTH - 50)
        self.lasers.append(Laser(es_horizontal, pos))
        audio.reproducir("laser_fase1", anti_spam_ms=100)

    def manejar_eventos(self, evento):
        # Escapar NO guarda partida.
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self.next_state = "MAIN_MENU"
            self.done = True

    def actualizar(self, dt):
        self.shake.actualizar(dt)
        self.compañero.actualizar(dt)
        teclas = pygame.key.get_pressed()
        self.jugador.actualizar(dt, teclas)

        intervalo_laser = max(0.3, 0.8 - (self.anomalias_recolectadas * 0.25))
        self.timer_laser += dt
        
        if self.timer_laser >= intervalo_laser: 
            self.spawn_laser()
            if self.anomalias_recolectadas == 1 and random.random() < 0.4: self.spawn_laser() 
            elif self.anomalias_recolectadas == 2:
                self.spawn_laser() 
                if random.random() < 0.5: self.spawn_laser() 
            self.timer_laser = 0.0

        for laser in self.lasers[:]:
            laser.actualizar(dt)
            if laser.terminado: self.lasers.remove(laser)
            elif laser.estado == "ACTIVO" and laser.rect.collidepoint(self.jugador.x, self.jugador.y):
                self.jugador.x = config.WIDTH / 2
                self.jugador.y = config.HEIGHT / 2
                self.shake.iniciar(intensidad=12, duracion=0.3)

        for anomalia in self.anomalias[:]:
            anomalia.actualizar(dt)
            if not anomalia.recolectada:
                dist = math.hypot(self.jugador.x - anomalia.x, self.jugador.y - anomalia.y)
                if dist < (self.jugador.radio_nucleo + anomalia.radio):
                    anomalia.recolectada = True
                    self.anomalias_recolectadas += 1
                    audio.reproducir("anomalia")
                    
                    if self.anomalias_recolectadas == 1:
                        self.compañero.mostrar_mensaje("¡Bien! Cuidado, el sistema está acelerando sus defensas.", id_voz="v_f1_mid")
                    elif self.anomalias_recolectadas == 2:
                        self.compañero.mostrar_mensaje("¡Solo falta una! ¡Cuidado con el ataque doble!", id_voz="v_f1_fin")
                        
                    if self.anomalias_recolectadas < 3: 
                        self.spawn_anomalia()
                    else: 
                        save_manager.guardar(2) # <--- GUARDA AL GANAR
                        self.done = True

    def dibujar(self, superficie):
        surf_temp = pygame.Surface((config.WIDTH, config.HEIGHT))
        surf_temp.fill(config.COLOR_BG)
        color_linea = (20, 20, 20)
        for x in range(0, config.WIDTH, 40): pygame.draw.line(surf_temp, color_linea, (x, 0), (x, config.HEIGHT))
        for y in range(0, config.HEIGHT, 40): pygame.draw.line(surf_temp, color_linea, (0, y), (config.WIDTH, y))
        
        for laser in self.lasers: laser.dibujar(surf_temp)
        for anomalia in self.anomalias: anomalia.dibujar(surf_temp)
        self.jugador.dibujar(surf_temp)

        ox, oy = self.shake.obtener_offset()
        superficie.blit(surf_temp, (ox, oy))
        self.compañero.dibujar(superficie)