import math
import random
import pygame
from utils.fonts import get_font
from states.base_state import BaseState
from utils.companion import CompanionUI
from utils import audio
from utils import save_manager
from utils.vfx import _CACHE, GlowCache, GradientCache, ProceduralUI
import config


class Regalo:
    def __init__(self, velocidad, jx):
        area_x = (config.WIDTH - 960) // 2
        self.rect = pygame.Rect(random.randint(area_x + 60, area_x + 960 - 60), -30, 30, 30)
        # Hacemos que un porcentaje de los regalos apunten hacia el jugador para que sea más accesible
        if random.random() < 0.35:
            self.rect.x = jx
        self.y = -30.0
        self.vy = velocidad

    def actualizar(self, dt):
        self.y += self.vy * dt
        self.rect.y = int(self.y)

    def dibujar(self, sup):
        cx, cy = self.rect.centerx, self.rect.centery
        GlowCache.blit(sup, cx, cy, 26, (255, 200, 70), intensity=0.45)

        # Caja principal con sombra interior y borde
        pygame.draw.rect(sup, (200, 25, 35), self.rect, border_radius=4)
        pygame.draw.rect(sup, (255, 80, 90), (self.rect.x + 2, self.rect.y + 2, 26, 8), border_radius=2)

        # Cintas cruzadas doradas/verdes
        pygame.draw.rect(sup, (30, 210, 70), (self.rect.x + 11, self.rect.y, 8, 30))
        pygame.draw.rect(sup, (30, 210, 70), (self.rect.x, self.rect.y + 11, 30, 8))
        pygame.draw.rect(sup, (255, 215, 0), (self.rect.x + 13, self.rect.y, 4, 30))
        pygame.draw.rect(sup, (255, 215, 0), (self.rect.x, self.rect.y + 13, 30, 4))

        # Moño superior
        pygame.draw.polygon(sup, (255, 215, 0), [
            (cx, self.rect.top),
            (cx - 8, self.rect.top - 6),
            (cx - 3, self.rect.top - 2)
        ])
        pygame.draw.polygon(sup, (255, 215, 0), [
            (cx, self.rect.top),
            (cx + 8, self.rect.top - 6),
            (cx + 3, self.rect.top - 2)
        ])


class XmasMinigame(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "MAIN_MENU"  # Cancela la cinemática si abortas
        self.compañero = CompanionUI()
        self.jugador_rect = pygame.Rect(config.WIDTH // 2 - 40, config.HEIGHT - 60, 80, 20)
        self.regalos = []
        self.score = 0
        self.regalos_perdidos = 0
        self.timer_spawn = 0.0
        self.ganado = False
        self.timer_victoria = 0.0
        self.es_partida = True
        self.fuente_ui = get_font(24, bold=True)
        self.bg_surf = self._get_aurora_bg()
        self.capas_nieve = [
            [(random.randint(0, config.WIDTH), random.randint(0, config.HEIGHT), spd, rad)
             for _ in range(cnt)]
            for cnt, spd, rad in [(30, 28.0, 1), (24, 52.0, 2), (16, 85.0, 3)]
        ]
        self.tiempo = 0.0

    @staticmethod
    def _get_aurora_bg():
        key = ("xmas_aurora_bg", config.WIDTH, config.HEIGHT)
        if key not in _CACHE:
            base = GradientCache.get_vertical(
                config.WIDTH, config.HEIGHT, (8, 18, 36), (18, 42, 62), vignette=True
            ).copy()
            # Bandas de aurora boreal pre-calculadas
            aurora = pygame.Surface((config.WIDTH, 220), pygame.SRCALPHA)
            for x in range(0, config.WIDTH, 4):
                onda = int(math.sin(x * 0.008) * 28 + math.cos(x * 0.019) * 14)
                y_top = 45 + onda
                for h in range(70):
                    alpha = int(42 * (1.0 - abs(h - 35) / 35.0))
                    col = (40, 230, 160, alpha) if (x // 4) % 2 == 0 else (70, 190, 255, alpha)
                    pygame.draw.line(aurora, col, (x, y_top + h), (x + 3, y_top + h))
            base.blit(aurora, (0, 0))
            _CACHE[key] = base
        return _CACHE[key]

    def startup(self):
        self.done = False
        self.next_state = "OUTRO_1"
        self.score, self.regalos_perdidos = 0, 0
        self.timer_spawn = 0.0
        self.regalos, self.ganado, self.timer_victoria = [], False, 0.0
        self.logros_obtenidos = save_manager.cargar().get("secretos", [])
        self.jugador_rect.x = config.WIDTH // 2 - 40
        self.tiempo = 0.0
        self.compañero.mostrar_mensaje("¡Hola San, feliz navidad! Ayúdame a atrapar 10 regalos, ¡no dejes que se nos caigan!")
        audio.reproducir_musica("assets/audio/fase1_nav.ogg", volumen=0.4)

    def manejar_eventos(self, evento):
        pass

    def actualizar(self, dt):
        self.tiempo += dt
        self.compañero.actualizar(dt)

        if self.ganado:
            self.timer_victoria += dt
            if self.timer_victoria > 1.5:
                save_manager.guardar(fase=2)
                self.next_state = "OUTRO_1"
                self.done = True
            return

        teclas = pygame.key.get_pressed()
        vel = 550 * dt
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.jugador_rect.x -= vel
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.jugador_rect.x += vel
        area_x = (config.WIDTH - 960) // 2
        if self.jugador_rect.left < area_x:
            self.jugador_rect.left = area_x
        if self.jugador_rect.right > area_x + 960:
            self.jugador_rect.right = area_x + 960

        intervalo = max(0.55, 1.3 - (self.score * 0.07))
        self.timer_spawn += dt
        if self.timer_spawn > intervalo:
            # Velocidad de caída moderada y equilibrada para facilitar el logro
            self.regalos.append(Regalo(115 + (self.score * 10), self.jugador_rect.centerx))
            self.timer_spawn = 0.0

        for r in self.regalos[:]:
            r.actualizar(dt)
            if r.rect.colliderect(self.jugador_rect):
                self.score += 1
                audio.reproducir("anomalia")
                self.regalos.remove(r)

                if self.score >= 10:
                    self.ganado = True
                    # Balance: Te permitimos que se te caiga 1 por accidente
                    if self.regalos_perdidos <= 1 and "L1" not in self.logros_obtenidos:
                        save_manager.guardar(secreto="L1")
                        self.compañero.mostrar_mensaje("¡LOGRO: Manos Ágiles! ¡Wao, qué manos! No se te escapa nada.")
                    else:
                        self.compañero.mostrar_mensaje("¡Bien hecho! Ya tenemos todos los regalos, ¡sigamos adelante!")

            elif r.y > config.HEIGHT:
                self.regalos.remove(r)
                self.regalos_perdidos += 1
                if self.score > 0:
                    self.score -= 1
                    audio.reproducir("explosion")
                    self.compañero.mostrar_mensaje("¡Uy, ese sonó fuerte! Se nos cayó uno (-1 pto), ¡no pasa nada, tú puedes!")

    def _dibujar_trineo(self, superficie):
        r = self.jugador_rect
        GlowCache.blit(superficie, r.centerx, r.centery, 48, (255, 200, 100), intensity=0.35)
        # Patines dorados inferiores
        pygame.draw.line(superficie, (255, 215, 0), (r.left - 6, r.bottom + 2), (r.right + 6, r.bottom + 2), 3)
        pygame.draw.arc(superficie, (255, 215, 0), (r.right - 2, r.top + 6, 14, 16), -math.pi / 2, math.pi / 2, 2)
        pygame.draw.arc(superficie, (255, 215, 0), (r.left - 12, r.top + 6, 14, 16), math.pi / 2, 3 * math.pi / 2, 2)
        # Cuerpo de madera cálida y borde festivo
        pygame.draw.rect(superficie, (165, 50, 40), r, border_radius=5)
        pygame.draw.rect(superficie, (255, 215, 0), r, 2, border_radius=5)

    def dibujar(self, superficie):
        superficie.blit(self.bg_surf, (0, 0))

        # 3 capas de nieve en paralaje
        for idx, capa in enumerate(self.capas_nieve):
            col = (180 + idx * 30, 205 + idx * 20, 255)
            for sx, sy, spd, rad in capa:
                px = int((sx + math.sin(self.tiempo * 1.5 + sy) * (8 + idx * 4)) % config.WIDTH)
                py = int((sy + self.tiempo * spd) % config.HEIGHT)
                pygame.draw.circle(superficie, col, (px, py), rad)

        for r in self.regalos:
            r.dibujar(superficie)

        self._dibujar_trineo(superficie)

        hud_rect = pygame.Rect(14, 14, 185, 42)
        ProceduralUI.draw_panel(
            superficie, hud_rect,
            bg_color=(12, 24, 38, 210),
            border_color=(255, 215, 0),
            cut=8,
            glow=False
        )
        txt = self.fuente_ui.render(f"Regalos: {self.score}/10", True, (255, 255, 255))
        superficie.blit(txt, (26, 21))
        self.compañero.dibujar(superficie, self.jugador_rect.y)
