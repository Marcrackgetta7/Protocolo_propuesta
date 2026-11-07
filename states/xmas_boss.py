import math
import random
import pygame
from utils.fonts import get_font
from states.base_state import BaseState
from entities.player import Player
from utils.companion import CompanionUI
from utils import audio
from utils import save_manager
from utils.vfx import GlowCache, GradientCache, BurstPool, ProceduralUI
import config


class BolaNieve:
    def __init__(self, x, y, vx, vy):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy

    def actualizar(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def dibujar(self, sup):
        cx, cy = int(self.x), int(self.y)
        GlowCache.blit(sup, cx, cy, 16, (140, 210, 255), intensity=0.55)
        pygame.draw.circle(sup, (220, 240, 255), (cx, cy), 8)
        pygame.draw.circle(sup, (255, 255, 255), (cx - 2, cy - 2), 4)


class RegaloBala:
    def __init__(self, x, y):
        self.x, self.y, self.vy = x, y, -350

    def actualizar(self, dt):
        self.y += self.vy * dt

    def dibujar(self, sup):
        cx, cy = int(self.x), int(self.y)
        GlowCache.blit(sup, cx, cy, 16, (255, 200, 60), intensity=0.55)
        pygame.draw.rect(sup, (220, 20, 20), (cx - 6, cy - 6, 12, 12), border_radius=2)
        pygame.draw.rect(sup, (255, 215, 0), (cx - 2, cy - 6, 4, 12))
        pygame.draw.rect(sup, (255, 215, 0), (cx - 6, cy - 2, 12, 4))


class ZonaCalor:
    def __init__(self, x, y):
        self.x, self.y, self.radio, self.timer = x, y, 60, 6.0

    def actualizar(self, dt):
        self.timer -= dt

    def dibujar(self, sup):
        cx, cy = int(self.x), int(self.y)
        pulso = 1.0 + 0.12 * math.sin(self.timer * 7.0)
        GlowCache.blit(sup, cx, cy, int(self.radio * 1.35 * pulso), (255, 110, 20), intensity=0.65)
        pygame.draw.circle(sup, (255, 160, 30), (cx, cy), int(12 * pulso))
        pygame.draw.circle(sup, (255, 230, 150), (cx, cy), 6)
        pygame.draw.circle(sup, (255, 90, 20), (cx, cy), self.radio, 2)
        pygame.draw.circle(sup, (255, 180, 60), (cx, cy), int(self.radio * 0.65), 1)


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

        self.ganado = False
        self.timer_victoria = 0.0
        self.se_congelo_alguna_vez = False
        self.es_partida = True
        self.fuente_ui = get_font(14, bold=True)

        self.bg_surf = GradientCache.get_vertical(
            config.WIDTH, config.HEIGHT, (10, 24, 42), (20, 44, 68), vignette=True
        )
        # Viñeta de escarcha pre-calculada para modular su alpha según self.congelacion
        self.frost_vignette = self._crear_frost_vignette()
        self.bursts = BurstPool(capacity=35)

    @staticmethod
    def _crear_frost_vignette():
        surf = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        steps = 16
        for i in range(steps):
            t = (i + 1) / steps
            alpha = int((t ** 2) * 28)
            pad_x = int((1.0 - t) * 140)
            pad_y = int((1.0 - t) * 90)
            rect = pygame.Rect(pad_x, pad_y, config.WIDTH - pad_x * 2, config.HEIGHT - pad_y * 2)
            pygame.draw.rect(surf, (130, 210, 255, alpha), rect, 14, border_radius=35)
        return surf

    def startup(self):
        self.done = False
        self.next_state = "OUTRO_4"
        self.jugador = Player(config.WIDTH / 2, config.HEIGHT - 150)
        self.vel_original = self.jugador.velocidad
        self.bolas, self.mis_balas, self.zonas_calor = [], [], []
        self.salud_boss, self.congelacion, self.congelado = 100, 0.0, False
        self.timer_descongelar = 0.0
        self.timer_disparo, self.timer_aoe, self.timer_ayuda, self.timer_bala_jugador = 0.0, 0.0, 0.0, 0.0
        self.se_congelo_alguna_vez, self.ganado, self.timer_victoria = False, False, 0.0
        self.logros_obtenidos = save_manager.cargar().get("secretos", [])

        self.compañero.mostrar_mensaje("¡Cuidado con la nieve! Mientras más te enfríes, más lento te moverás y dispararás.")
        audio.reproducir_musica("assets/audio/Jefe_nav.ogg", volumen=0.5)

    def manejar_eventos(self, evento):
        pass

    def actualizar(self, dt):
        self.compañero.actualizar(dt)
        self.bursts.update(dt)

        if self.ganado:
            self.timer_victoria += dt
            if self.timer_victoria > 1.5:
                save_manager.guardar(fase=5)
                self.next_state = "OUTRO_4"
                self.done = True
            return

        teclas = pygame.key.get_pressed()
        factor_salud = max(0.1, self.salud_boss / 100.0)

        if self.congelado:
            self.timer_descongelar -= dt
            self.salud_boss = min(100, self.salud_boss + (5 * dt))
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

        if self.jugador.x < 20:
            self.jugador.x = 20
        if self.jugador.x > config.WIDTH - 20:
            self.jugador.x = config.WIDTH - 20
        if self.jugador.y < config.HEIGHT // 2 + 50:
            self.jugador.y = config.HEIGHT // 2 + 50
        if self.jugador.y > config.HEIGHT - 20:
            self.jugador.y = config.HEIGHT - 20

        self.timer_ayuda += dt
        if self.timer_ayuda > 8.0:
            self.zonas_calor.append(
                ZonaCalor(
                    random.randint(100, config.WIDTH - 100),
                    random.randint(config.HEIGHT // 2 + 50, config.HEIGHT - 50)
                )
            )
            self.timer_ayuda = 0.0
            self.compañero.mostrar_mensaje("¡Te envié un núcleo de calor! Quédate ahí para descongelarte.")

        for z in self.zonas_calor[:]:
            z.actualizar(dt)
            if z.timer <= 0:
                self.zonas_calor.remove(z)
            elif math.hypot(self.jugador.x - z.x, self.jugador.y - z.y) < z.radio:
                self.congelacion = max(0, self.congelacion - (40 * dt))

        self.boss_x = (config.WIDTH / 2) + math.sin(pygame.time.get_ticks() * 0.002) * 200

        self.timer_disparo += dt
        if self.timer_disparo > 0.1 + (0.4 * factor_salud):
            self.bolas.append(
                BolaNieve(
                    self.boss_x, self.boss_y + 30,
                    random.randint(-100, 100),
                    200 + (100 * (1 - factor_salud))
                )
            )
            self.timer_disparo = 0.0

        self.timer_aoe += dt
        if self.timer_aoe > 1.5 + (3.0 * factor_salud):
            for i in range(12):
                ang = i * (math.pi / 6)
                self.bolas.append(
                    BolaNieve(self.boss_x, self.boss_y + 30, math.cos(ang) * 200, math.sin(ang) * 200)
                )
            self.timer_aoe = 0.0
            audio.reproducir("boss_area", anti_spam_ms=300)

        for b in self.mis_balas[:]:
            b.actualizar(dt)
            if b.y < 0:
                self.mis_balas.remove(b)
            elif math.hypot(self.boss_x - b.x, self.boss_y - b.y) < 40:
                self.salud_boss -= 2
                if b in self.mis_balas:
                    self.mis_balas.remove(b)

        for b in self.bolas[:]:
            b.actualizar(dt)
            if b.y > config.HEIGHT or b.x < 0 or b.x > config.WIDTH:
                self.bolas.remove(b)
            elif math.hypot(self.jugador.x - b.x, self.jugador.y - b.y) < 15:
                if b in self.bolas:
                    self.bolas.remove(b)
                if self.congelado:
                    self.bursts.emit(
                        b.x, b.y, count=7,
                        colors=[(180, 230, 255), (255, 255, 255)],
                        heart_chance=0.0, speed_range=(35, 110)
                    )
                else:
                    self.congelacion += 15
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
            else:
                self.compañero.mostrar_mensaje("¡Muñeco de nieve destruido! Avanzando...")

    def _dibujar_boss(self, superficie):
        bx, by = int(self.boss_x), int(self.boss_y)
        GlowCache.blit(superficie, bx, by - 10, 65, (120, 200, 255), intensity=0.6)

        # Torso y cabeza con sombreado
        pygame.draw.circle(superficie, (205, 225, 250), (bx, by), 30)
        pygame.draw.circle(superficie, (255, 255, 255), (bx - 4, by - 4), 26)
        pygame.draw.circle(superficie, (205, 225, 250), (bx, by - 40), 20)
        pygame.draw.circle(superficie, (255, 255, 255), (bx - 3, by - 42), 17)

        # Botones de carbón en el torso
        for ky in (by - 12, by, by + 12):
            pygame.draw.circle(superficie, (25, 30, 40), (bx, ky), 3)

        # Ojos brillantes furiosos y cejas fruncidas
        pygame.draw.circle(superficie, (255, 50, 50), (bx - 7, by - 42), 3)
        pygame.draw.circle(superficie, (255, 50, 50), (bx + 7, by - 42), 3)
        pygame.draw.line(superficie, (20, 20, 30), (bx - 12, by - 48), (bx - 3, by - 44), 3)
        pygame.draw.line(superficie, (20, 20, 30), (bx + 12, by - 48), (bx + 3, by - 44), 3)

        # Nariz de zanahoria
        pygame.draw.polygon(superficie, (255, 130, 20), [(bx, by - 38), (bx + 14, by - 35), (bx, by - 33)])

        # Sombrero de copa con cinta roja
        pygame.draw.rect(superficie, (25, 25, 35), (bx - 22, by - 60, 44, 5))
        pygame.draw.rect(superficie, (25, 25, 35), (bx - 14, by - 82, 28, 22))
        pygame.draw.rect(superficie, (220, 30, 40), (bx - 14, by - 65, 28, 5))

    def dibujar(self, superficie):
        superficie.blit(self.bg_surf, (0, 0))

        for z in self.zonas_calor:
            z.dibujar(superficie)
        for b in self.mis_balas + self.bolas:
            b.dibujar(superficie)
        self.bursts.draw(superficie)

        if self.congelado:
            GlowCache.blit(superficie, self.jugador.x, self.jugador.y, 35, (130, 210, 255), intensity=0.8)
            pygame.draw.rect(
                superficie, (150, 215, 255),
                (int(self.jugador.x) - 15, int(self.jugador.y) - 15, 30, 30),
                border_radius=5
            )
            pygame.draw.rect(
                superficie, (255, 255, 255),
                (int(self.jugador.x) - 15, int(self.jugador.y) - 15, 30, 30), 2,
                border_radius=5
            )

        self.jugador.dibujar(superficie)
        self._dibujar_boss(superficie)

        # Viñeta de escarcha reactiva a self.congelacion
        if self.congelacion > 2:
            self.frost_vignette.set_alpha(min(255, int(self.congelacion * 2.5)))
            superficie.blit(self.frost_vignette, (0, 0))

        # Barra de salud del jefe
        bar_boss = pygame.Rect(config.WIDTH // 2 - 100, 20, 200, 15)
        pygame.draw.rect(superficie, (30, 40, 55), bar_boss)
        pygame.draw.rect(superficie, (235, 50, 60), (bar_boss.x, bar_boss.y, int(max(0, self.salud_boss) * 2), 15))
        pygame.draw.rect(superficie, (255, 255, 255), bar_boss, 2)

        # Barra de frío del jugador
        superficie.blit(self.fuente_ui.render("FRÍO:", True, (150, 210, 255)), (20, 20))
        pygame.draw.rect(superficie, (25, 45, 75), (70, 20, 100, 15))
        pygame.draw.rect(superficie, (0, 175, 255), (70, 20, int(self.congelacion), 15))
        pygame.draw.rect(superficie, (200, 235, 255), (70, 20, 100, 15), 1)

        self.compañero.dibujar(superficie, self.jugador.y)
