import math
import random
import pygame
from utils.fonts import get_font
from states.base_state import BaseState
from entities.player import Player
from utils.companion import CompanionUI
from utils.vfx import _CACHE, ScreenShake, GlowCache, GradientCache, BurstPool, ProceduralUI
from utils import audio
from utils import save_manager
import config


class BalaJugador:
    def __init__(self, x, y):
        self.x, self.y, self.vy, self.radio = x, y, -400, 4

    def actualizar(self, dt):
        self.y += self.vy * dt

    def dibujar(self, sup):
        cx, cy = int(self.x), int(self.y)
        GlowCache.blit(sup, cx, cy, 14, (160, 220, 255), intensity=0.65)
        pygame.draw.line(sup, (160, 220, 255), (cx, cy), (cx, cy + 10), 3)
        pygame.draw.circle(sup, config.COLOR_TEXT, (cx, cy), self.radio)


class ProyectilBoss:
    def __init__(self, x, y, tx, ty, speed=250):
        self.x, self.y = float(x), float(y)
        angulo = math.atan2(ty - y, tx - x)
        self.vx, self.vy = math.cos(angulo) * speed, math.sin(angulo) * speed
        self.radio = 6

    def actualizar(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def dibujar(self, sup):
        cx, cy = int(self.x), int(self.y)
        GlowCache.blit(sup, cx, cy, 16, config.COLOR_ENERGY, intensity=0.65)
        pygame.draw.circle(sup, config.COLOR_ENERGY, (cx, cy), self.radio)
        pygame.draw.circle(sup, (255, 220, 235), (cx, cy), 3)


class BarridoLaser:
    def __init__(self, speed, width):
        self.w, self.x, self.vx = int(width), -width, speed

    @staticmethod
    def _get_sweep_surf(w):
        w_key = max(20, int(w))
        key = ("sweep_laser", w_key, config.HEIGHT)
        if key not in _CACHE:
            surf = pygame.Surface((w_key, config.HEIGHT), pygame.SRCALPHA)
            mitad = w_key / 2.0
            for ix in range(w_key):
                dist = abs(ix - mitad) / max(1.0, mitad)
                alpha = int(175 * ((1.0 - dist) ** 1.6))
                pygame.draw.line(surf, (255, 10, 30, alpha), (ix, 0), (ix, config.HEIGHT))
            pygame.draw.rect(surf, (255, 255, 255, 240), (w_key // 2 - 5, 0, 10, config.HEIGHT))
            _CACHE[key] = surf
        return _CACHE[key]

    def actualizar(self, dt):
        self.x += self.vx * dt

    def dibujar(self, sup):
        surf = self._get_sweep_surf(self.w)
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
        self.angulo_nucleo = 0.0

        self.disparos_hechos = 0
        self.logro_pacifista_entregado = False

        self.estado = "INTRO"
        self.yo_x, self.yo_y = -100, -100
        self.es_partida = True
        self.fuente_ui = get_font(16, bold=True)
        self.boss_x, self.boss_y = config.WIDTH / 2, 100

        self.surf_temp = pygame.Surface((config.WIDTH, config.HEIGHT))
        self.bg_surf = GradientCache.get_vertical(
            config.WIDTH, config.HEIGHT, (18, 4, 10), (6, 6, 12), vignette=True
        )
        self.bursts = BurstPool(capacity=60)

    def startup(self):
        self.done = False
        self.next_state = "CREDITS"
        self.jugador = Player(config.WIDTH / 2, config.HEIGHT - 100)
        self.proyectiles_boss, self.balas_jugador, self.barridos = [], [], []
        self.salud_jugador, self.escudo_jugador, self.salud_boss = 100, 100, 100
        self.estado = "INTRO"
        self.timer_disparo_jugador = 0.0
        self.timer_fase, self.timer_disparo, self.timer_radial, self.timer_barrido = 0.0, 0.0, 0.0, 0.0
        self.disparos_hechos = 0
        self.hit_flash_timer = 0.0
        self.angulo_nucleo = 0.0

        datos_guardados = save_manager.cargar()
        self.logro_pacifista_entregado = "Pacifista" in datos_guardados.get("secretos", [])

        self.yo_x, self.yo_y = -100, -100
        self.boss_x, self.boss_y = config.WIDTH / 2, 100
        self.compañero.mostrar_mensaje("¡Ahí está el origen del Glitch! ¡Eliminémoslo juntos!", id_voz="v_f3_in")
        audio.reproducir_musica("assets/audio/Jefe_dark.ogg", volumen=0.5)

    def manejar_eventos(self, evento):
        pass

    def actualizar(self, dt):
        self.shake.actualizar(dt)
        self.compañero.actualizar(dt)
        self.bursts.update(dt)
        teclas = pygame.key.get_pressed()

        # Escalado de presión por tiempo en combate y desgaste de escudo/salud de la jugadora
        desgaste_jugador = 1.0 - max(0.0, (self.escudo_jugador + max(0.0, self.salud_jugador - 20.0)) / 180.0)
        if self.estado == "COMBAT":
            progreso_tiempo = min(1.0, self.timer_fase / 35.0)
        elif self.estado in ["WARNING", "SACRIFICE", "GLITCH"]:
            progreso_tiempo = 1.0
        else:
            progreso_tiempo = 0.0
        presion = min(0.99, max(progreso_tiempo, desgaste_jugador * 0.85))
        factor_salud = max(0.01, 1.0 - presion)
        self.angulo_nucleo += (1.8 + (1.0 - factor_salud) * 3.5) * dt

        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt

        if self.estado in ["INTRO", "COMBAT", "WARNING"]:
            self.jugador.actualizar(dt, teclas)
            if self.jugador.x < 20:
                self.jugador.x = 20
            if self.jugador.x > config.WIDTH - 20:
                self.jugador.x = config.WIDTH - 20
            if self.jugador.y < config.HEIGHT // 2 + 50:
                self.jugador.y = config.HEIGHT // 2 + 50
            if self.jugador.y > config.HEIGHT - 20:
                self.jugador.y = config.HEIGHT - 20

            # --- ARREGLO LOGRO PACIFISTA ---
            # El gatillo está 100% apagado durante la "INTRO".
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
                self.compañero.mostrar_mensaje("¡Tú concéntrate en bajarle la vida! Yo mantengo tus escudos, tranquila.", id_voz="v_f3_esc")

        elif self.estado == "COMBAT":
            if self.timer_fase > 15.0 and self.disparos_hechos == 0 and not self.logro_pacifista_entregado:
                save_manager.guardar(secreto="Pacifista")
                self.logro_pacifista_entregado = True
                self.compañero.mostrar_mensaje("¡LOGRO: Pacifista! ¡15s esquivando todo sin disparar, estás loca!")

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

            if self.salud_jugador <= 20:
                self.estado = "WARNING"
                self.timer_fase = 0.0
                audio.reproducir("laser_final")
                self.compañero.mostrar_mensaje("¡NO! ¡Está cargando un láser de borrado total, tu escudo no va a soportar!", id_voz="v_f3_alert")
                self.shake.iniciar(8, 2.0)

        elif self.estado == "WARNING":
            if self.timer_fase > 3.0:
                self.estado = "SACRIFICE"
                self.timer_fase = 0.0
                self.yo_x, self.yo_y = self.jugador.x, self.jugador.y - 50
                self.shake.iniciar(25, 4.0)
                self.compañero.mostrar_mensaje("¡Tus escudos cayeron! No voy a dejar que te borren... ¡Yo te cubriré aunque me cueste la vida!", id_voz="v_f3_crit")

        elif self.estado == "SACRIFICE":
            if random.random() < 0.45:
                self.bursts.emit(
                    self.yo_x, self.yo_y - 12, count=4,
                    colors=[(0, 255, 120), config.COLOR_DANGER, (255, 255, 255)],
                    heart_chance=0.0, speed_range=(70, 220)
                )
            if 1.5 < self.timer_fase < 1.6:
                self.compañero.mostrar_mensaje("¡Desviando todo el rayo hacia mi consola! ¡Aguanta un poco más, por favor!", id_voz="v_f3_sac1")
            elif 3.5 < self.timer_fase < 3.6:
                self.compañero.mostrar_mensaje("¡Mi sistema se quema, pero a ti no te tocará! ¡Forzando apagado...!", id_voz="v_f3_sac2")
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
            if b.y < 0:
                self.balas_jugador.remove(b)
            elif math.hypot(self.boss_x - b.x, self.boss_y - b.y) < 50:
                self.hit_flash_timer = 0.1
                self.bursts.emit(b.x, b.y, count=5, colors=[config.COLOR_DANGER, (255, 220, 220)], heart_chance=0.0)
                if b in self.balas_jugador:
                    self.balas_jugador.remove(b)
                if self.salud_boss > 35.0:
                    resistencia = max(0.15, (self.salud_boss - 35.0) / 65.0)
                    self.salud_boss = max(35.0, self.salud_boss - 0.15 * resistencia)

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

        for barrido in self.barridos[:]:
            barrido.actualizar(dt)
            if barrido.x > config.WIDTH:
                self.barridos.remove(barrido)
            elif self.estado == "COMBAT":
                r = self.jugador.radio_nucleo
                if barrido.x - r < self.jugador.x < barrido.x + barrido.w + r:
                    self.shake.iniciar(10, 0.1)
                    if self.escudo_jugador > 0:
                        self.escudo_jugador -= 30 * dt
                    else:
                        self.salud_jugador -= 30 * dt

    def _dibujar_nucleo(self, superficie):
        bx, by = int(self.boss_x), int(self.boss_y)
        flash = self.hit_flash_timer > 0
        pulso = 1.0 + 0.12 * math.sin(self.angulo_nucleo * 3.0)

        GlowCache.blit(
            superficie, bx, by, int(95 * pulso),
            (255, 255, 255) if flash else config.COLOR_DANGER,
            intensity=0.75
        )

        # Anillo octogonal exterior giratorio
        pts_ext = [
            (bx + math.cos(self.angulo_nucleo + i * math.pi / 4) * 54,
             by + math.sin(self.angulo_nucleo + i * math.pi / 4) * 54)
            for i in range(8)
        ]
        # Anillo hexagonal interior contra-rotatorio
        pts_int = [
            (bx + math.cos(-self.angulo_nucleo * 1.4 + i * math.pi / 3) * 38,
             by + math.sin(-self.angulo_nucleo * 1.4 + i * math.pi / 3) * 38)
            for i in range(6)
        ]

        color_ext = (255, 255, 255) if flash else (110, 0, 15)
        color_int = (255, 255, 255) if flash else config.COLOR_DANGER
        pygame.draw.polygon(superficie, color_ext, pts_ext)
        pygame.draw.polygon(superficie, (255, 90, 90), pts_ext, 2)
        pygame.draw.polygon(superficie, (50, 0, 10), pts_int)
        pygame.draw.polygon(superficie, config.COLOR_ENERGY, pts_int, 2)

        pygame.draw.circle(superficie, color_int, (bx, by), int(24 * pulso))
        pygame.draw.circle(superficie, (255, 230, 230), (bx, by), int(10 * pulso))

    def dibujar(self, superficie):
        self.surf_temp.blit(self.bg_surf, (0, 0))

        for b in self.balas_jugador:
            b.dibujar(self.surf_temp)
        self.jugador.dibujar(self.surf_temp)

        # Escudo energético del jugador si tiene escudo > 0
        if self.escudo_jugador > 0 and self.estado in ["INTRO", "COMBAT"]:
            pygame.draw.circle(
                self.surf_temp, (0, 200, 255),
                (int(self.jugador.x), int(self.jugador.y)), 18, 1
            )

        self._dibujar_nucleo(self.surf_temp)

        if self.estado == "WARNING":
            pulso_w = int(150 + 100 * math.sin(self.timer_fase * 18.0))
            jx = int(self.jugador.x)
            pygame.draw.rect(
                self.surf_temp, (pulso_w, 60, 60),
                (jx - 40, int(self.boss_y), 80, config.HEIGHT), 2
            )
            pygame.draw.line(
                self.surf_temp, config.COLOR_DANGER,
                (jx, int(self.boss_y)), (jx, config.HEIGHT), 1
            )

        elif self.estado == "SACRIFICE":
            yx, yy = int(self.yo_x), int(self.yo_y)
            by = int(self.boss_y)

            # Colosal rayo de purga impactando contra el escudo del compañero
            GlowCache.blit(self.surf_temp, yx, (by + yy) // 2, 110, config.COLOR_DANGER, intensity=0.8)
            pygame.draw.rect(self.surf_temp, config.COLOR_DANGER, (yx - 42, by, 84, yy - by))
            pygame.draw.rect(self.surf_temp, (255, 235, 235), (yx - 18, by, 36, yy - by))

            # Escudo hexagonal verde brillante y arcos de desviación
            r_esc = min(145, 58 + int(self.timer_fase * 18))
            GlowCache.blit(self.surf_temp, yx, yy, r_esc, (0, 255, 110), intensity=0.85)
            pts_hex = [
                (yx + math.cos(self.timer_fase * 4.0 + i * math.pi / 3) * (r_esc * 0.65),
                 yy + math.sin(self.timer_fase * 4.0 + i * math.pi / 3) * (r_esc * 0.65))
                for i in range(6)
            ]
            pygame.draw.polygon(self.surf_temp, (0, 255, 120), pts_hex, 3)
            pygame.draw.circle(self.surf_temp, (255, 255, 255), (yx, yy), random.randint(28, 48), 2)
            pygame.draw.circle(self.surf_temp, (0, 255, 110), (yx, yy), 12)

        elif self.estado == "GLITCH":
            for _ in range(30):
                rx = random.randint(0, config.WIDTH)
                ry = random.randint(0, config.HEIGHT)
                rw = random.randint(10, 300)
                rh = random.randint(5, 80)
                pygame.draw.rect(
                    self.surf_temp,
                    random.choice([config.COLOR_DANGER, (0, 255, 100), (200, 200, 200)]),
                    (rx, ry, rw, rh)
                )

        for p in self.proyectiles_boss:
            p.dibujar(self.surf_temp)
        for barrido in self.barridos:
            barrido.dibujar(self.surf_temp)
        self.bursts.draw(self.surf_temp)

        # HUD Jugador y Jefe
        hud_izq = pygame.Rect(14, 14, 155, 58)
        ProceduralUI.draw_panel(
            self.surf_temp, hud_izq,
            bg_color=(14, 10, 20, 210), border_color=(0, 200, 255), cut=8, glow=False
        )
        self.surf_temp.blit(
            self.fuente_ui.render(f"SALUD: {max(0, int(self.salud_jugador))}%", True, config.COLOR_TEXT),
            (24, 20)
        )
        self.surf_temp.blit(
            self.fuente_ui.render(f"ESCUDO: {max(0, int(self.escudo_jugador))}%", True, (0, 200, 255)),
            (24, 44)
        )

        hud_der = pygame.Rect(config.WIDTH - 165, 14, 150, 52)
        ProceduralUI.draw_panel(
            self.surf_temp, hud_der,
            bg_color=(20, 8, 14, 210), border_color=config.COLOR_DANGER, cut=8, glow=False
        )
        self.surf_temp.blit(
            self.fuente_ui.render(f"NÚCLEO: {max(1, int(self.salud_boss))}%", True, config.COLOR_DANGER),
            (config.WIDTH - 152, 20)
        )
        pygame.draw.rect(self.surf_temp, (50, 0, 0), (config.WIDTH - 152, 45, 120, 10))
        pygame.draw.rect(
            self.surf_temp, config.COLOR_DANGER,
            (config.WIDTH - 152, 45, int(120 * (self.salud_boss / 100.0)), 10)
        )

        ox, oy = self.shake.obtener_offset()
        superficie.blit(self.surf_temp, (ox, oy))

        if self.estado != "GLITCH":
            self.compañero.dibujar(superficie, self.jugador.y)
