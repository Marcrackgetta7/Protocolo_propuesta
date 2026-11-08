import math
import random
import pygame
from utils.fonts import get_font
from states.base_state import BaseState
from entities.player import Player
from entities.anomaly import Anomaly
from entities.laser import Laser
from utils.vfx import _CACHE, ScreenShake, GlowCache, GradientCache, BurstPool, ProceduralUI
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
        self.pulso_grid = 0.0
        self.fuente_ui = get_font(24, bold=True)

        self.surf_temp = pygame.Surface((config.WIDTH, config.HEIGHT))
        self.bg_grid = self._get_cyber_grid()
        self.bursts = BurstPool(capacity=45)

    @staticmethod
    def _get_cyber_grid():
        key = ("cyber_grid_bg", config.WIDTH, config.HEIGHT)
        if key not in _CACHE:
            surf = GradientCache.get_vertical(
                config.WIDTH, config.HEIGHT, (6, 6, 12), (14, 4, 12), vignette=True
            ).copy()
            color_linea = (22, 18, 28)
            color_nodo = (65, 25, 45)
            for x in range(0, config.WIDTH, 40):
                pygame.draw.line(surf, color_linea, (x, 0), (x, config.HEIGHT))
            for y in range(0, config.HEIGHT, 40):
                pygame.draw.line(surf, color_linea, (0, y), (config.WIDTH, y))
            for x in range(0, config.WIDTH, 40):
                for y in range(0, config.HEIGHT, 40):
                    pygame.draw.circle(surf, color_nodo, (x, y), 2)
            _CACHE[key] = surf
        return _CACHE[key]

    def startup(self):
        self.done = False
        self.next_state = "OUTRO_5"
        self.jugador = Player(config.WIDTH / 2, config.HEIGHT / 2)
        self.anomalias, self.lasers = [], []
        self.anomalias_recolectadas, self.timer_laser = 0, 0.0
        self.golpes_laser, self.ganado, self.timer_victoria = 0, False, 0.0
        self.pulso_grid = 0.0
        self.logros_obtenidos = save_manager.cargar().get("secretos", [])

        self.spawn_anomalia()
        self.compañero.mostrar_mensaje("Tranquila, estoy contigo. Muévete rápido, yo te cubro.", id_voz="v_f1_in")
        audio.reproducir_musica("assets/audio/Fase1_dark.ogg", volumen=0.4)

    def spawn_anomalia(self):
        distancia = 0
        x, y = 0, 0
        while distancia < 250:
            x, y = random.randint(50, config.WIDTH - 50), random.randint(50, config.HEIGHT - 50)
            if not self.jugador:
                break
            distancia = math.hypot(self.jugador.x - x, self.jugador.y - y)
        self.anomalias.append(Anomaly(x, y))

    def spawn_laser(self):
        es_horizontal = random.choice([True, False])
        pos = random.randint(50, config.HEIGHT - 50) if es_horizontal else random.randint(50, config.WIDTH - 50)
        l = Laser(es_horizontal, pos)
        factor = self.anomalias_recolectadas * 0.05
        l.tiempo_aviso = max(0.60, 0.85 - factor)
        l.tiempo_activo = max(0.25, 0.35 - factor / 2)
        self.lasers.append(l)
        self.pulso_grid = 1.0
        audio.reproducir("laser_fase1", anti_spam_ms=100)

    def manejar_eventos(self, evento):
        pass

    def actualizar(self, dt):
        self.shake.actualizar(dt)
        self.compañero.actualizar(dt)
        self.bursts.update(dt)
        if self.pulso_grid > 0:
            self.pulso_grid = max(0.0, self.pulso_grid - dt * 2.5)

        if self.ganado:
            self.timer_victoria += dt
            if self.timer_victoria > 1.5:
                save_manager.guardar(fase=6)
                self.next_state = "OUTRO_5"
                self.done = True
            return

        teclas = pygame.key.get_pressed()
        self.jugador.actualizar(dt, teclas)

        if self.jugador.x < 20:
            self.jugador.x = 20
        if self.jugador.x > config.WIDTH - 20:
            self.jugador.x = config.WIDTH - 20
        if self.jugador.y < 20:
            self.jugador.y = 20
        if self.jugador.y > config.HEIGHT - 20:
            self.jugador.y = config.HEIGHT - 20

        intervalo_laser = max(0.55, 1.0 - (self.anomalias_recolectadas * 0.1))
        self.timer_laser += dt
        if self.timer_laser >= intervalo_laser:
            self.spawn_laser()
            if self.anomalias_recolectadas >= 2 and random.random() < 0.3:
                self.spawn_laser()
            elif self.anomalias_recolectadas >= 4 and random.random() < 0.4:
                self.spawn_laser()
            self.timer_laser = 0.0

        for laser in self.lasers[:]:
            laser.actualizar(dt)
            if laser.terminado:
                self.lasers.remove(laser)
            elif laser.estado == "ACTIVO" and laser.rect.collidepoint(self.jugador.x, self.jugador.y):
                self.bursts.emit(
                    self.jugador.x, self.jugador.y, count=18,
                    colors=[config.COLOR_DANGER, (255, 160, 160)], heart_chance=0.0
                )
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
                    self.bursts.emit(
                        anomalia.x, anomalia.y, count=16,
                        colors=[config.COLOR_ENERGY, (255, 180, 220)], heart_chance=0.0
                    )
                    audio.reproducir("anomalia")

                    if self.anomalias_recolectadas == 2:
                        self.compañero.mostrar_mensaje("¡Eso es, ya tienes dos! Ojo, el Glitch se enojó y está acelerando...", id_voz="v_f1_mid")
                    elif self.anomalias_recolectadas == 4:
                        self.compañero.mostrar_mensaje("¡Solo falta una para salir! ¡Cuidado, viene una ráfaga doble!", id_voz="v_f1_fin")
                    if self.anomalias_recolectadas < 5:
                        self.spawn_anomalia()
                    else:
                        self.ganado = True
                        if self.golpes_laser == 0 and "L5" not in self.logros_obtenidos:
                            save_manager.guardar(secreto="L5")
                            self.compañero.mostrar_mensaje("¡LOGRO: Fantasma Digital! ¡Ni un solo láser te rozó, eres increíble!")
                        else:
                            self.compañero.mostrar_mensaje("¡Lo lograste! Abriendo un túnel seguro, ¡te saco de ahí ya!")

    def dibujar(self, superficie):
        self.surf_temp.blit(self.bg_grid, (0, 0))

        # Pulso reactivo en intersecciones cuando se dispara un láser
        if self.pulso_grid > 0.05:
            col_p = (int(180 * self.pulso_grid), int(20 * self.pulso_grid), int(60 * self.pulso_grid))
            for x in range(80, config.WIDTH, 160):
                for y in range(80, config.HEIGHT, 160):
                    pygame.draw.circle(self.surf_temp, col_p, (x, y), 3)

        for laser in self.lasers:
            laser.dibujar(self.surf_temp)
        for anomalia in self.anomalias:
            anomalia.dibujar(self.surf_temp)
        self.jugador.dibujar(self.surf_temp)
        self.bursts.draw(self.surf_temp)

        # HUD estilizado
        hud_rect = pygame.Rect(14, 14, 210, 42)
        ProceduralUI.draw_panel(
            self.surf_temp, hud_rect,
            bg_color=(16, 10, 22, 215),
            border_color=config.COLOR_ENERGY,
            cut=8,
            glow=False
        )
        txt = self.fuente_ui.render(f"Anomalías: {self.anomalias_recolectadas}/5", True, config.COLOR_ENERGY)
        self.surf_temp.blit(txt, (26, 21))

        ox, oy = self.shake.obtener_offset()
        superficie.blit(self.surf_temp, (ox, oy))
        self.compañero.dibujar(superficie, self.jugador.y)
