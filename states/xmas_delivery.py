import math
import random
import pygame
from utils.fonts import get_font
from states.base_state import BaseState
from entities.player import Player
from utils.companion import CompanionUI
from utils import audio
from utils import save_manager
from utils.vfx import _CACHE, GlowCache, GradientCache, FloatingParticles, ProceduralUI
import config


class ObstaculoNavidad:
    """Obstáculo pequeño con renderizado procedural en caché y hitbox ajustado."""
    def __init__(self, x, y, variante=0):
        self.x = int(x)
        self.y = int(y)
        self.variante = variante
        # Hitbox ajustado (18x18) centrado en la base para no penalizar roces visuales
        self.hitbox = pygame.Rect(self.x - 9, self.y - 9, 18, 18)
        self.sprite = self._get_obstacle_surf(variante)

    @staticmethod
    def _get_obstacle_surf(variante):
        key = ("xmas_delivery_obstacle", variante)
        if key not in _CACHE:
            surf = pygame.Surface((36, 40), pygame.SRCALPHA)
            cx, cy = 18, 22
            if variante == 0:
                # Pino nevado con esferas festivas
                pygame.draw.ellipse(surf, (8, 16, 28, 120), (6, 28, 24, 10))
                pygame.draw.rect(surf, (95, 52, 28), (cx - 3, 25, 6, 9), border_radius=1)
                capas = [
                    ([(cx, 10), (cx - 14, 28), (cx + 14, 28)], (24, 105, 58), (225, 242, 255)),
                    ([(cx, 5), (cx - 11, 21), (cx + 11, 21)], (32, 130, 70), (235, 248, 255)),
                    ([(cx, 1), (cx - 8, 14), (cx + 8, 14)], (42, 155, 82), (245, 252, 255)),
                ]
                for pts, col_hoja, col_nieve in capas:
                    pygame.draw.polygon(surf, col_hoja, pts)
                    pygame.draw.lines(surf, col_nieve, False, [pts[1], pts[0], pts[2]], 2)
                # Esferas decorativas y estrella superior
                pygame.draw.circle(surf, (255, 65, 65), (cx - 5, 19), 2)
                pygame.draw.circle(surf, (255, 215, 0), (cx + 5, 23), 2)
                pygame.draw.circle(surf, (110, 215, 255), (cx + 2, 13), 2)
                pygame.draw.circle(surf, (255, 230, 90), (cx, 2), 2)
            else:
                # Roca de hielo / montículo escarchado
                pygame.draw.ellipse(surf, (8, 16, 28, 120), (5, 27, 26, 10))
                pts_base = [(6, 30), (9, 16), (17, 10), (26, 15), (30, 30)]
                pts_luz = [(9, 16), (17, 10), (22, 18), (13, 28)]
                pygame.draw.polygon(surf, (115, 175, 230), pts_base)
                pygame.draw.polygon(surf, (185, 228, 255), pts_luz)
                pygame.draw.polygon(surf, (235, 248, 255), pts_base, 2)
                pygame.draw.line(surf, (255, 255, 255), (13, 16), (18, 24), 2)
            _CACHE[key] = surf
        return _CACHE[key]

    def dibujar(self, sup):
        sup.blit(self.sprite, (self.x - 18, self.y - 22))


class Casa:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 60, 60)
        self.entregado = False
        self.fase_humo = random.uniform(0.0, math.tau)

    def dibujar(self, sup, tiempo=0.0):
        r = self.rect
        # Chimenea y humo procedural
        chim_x, chim_y = r.right - 16, r.top - 22
        pygame.draw.rect(sup, (110, 45, 35), (chim_x, chim_y, 10, 18))
        for i in range(3):
            prog = ((tiempo * 0.9 + i * 0.33 + self.fase_humo) % 1.0)
            hx = chim_x + 5 + int(math.sin(tiempo * 2.5 + i) * 6 * prog)
            hy = chim_y - int(prog * 24)
            rad = int(3 + prog * 4)
            col_h = int(190 * (1.0 - prog * 0.5))
            pygame.draw.circle(sup, (col_h, col_h, min(255, col_h + 15)), (hx, hy), rad)

        # Fachada de la cabaña
        color_pared = (50, 165, 75) if self.entregado else (165, 45, 45)
        if self.entregado:
            GlowCache.blit(sup, r.centerx, r.centery, 58, (255, 210, 90), intensity=0.55)
        pygame.draw.rect(sup, color_pared, r, border_radius=3)
        pygame.draw.rect(sup, (235, 240, 255), r, 2, border_radius=3)

        # Puerta y ventanas (se iluminan con luz cálida al entregar)
        pygame.draw.rect(sup, (85, 45, 25), (r.centerx - 7, r.bottom - 22, 14, 22))
        col_ventana = (255, 230, 110) if self.entregado else (40, 55, 75)
        win1 = pygame.Rect(r.left + 8, r.top + 14, 14, 14)
        win2 = pygame.Rect(r.right - 22, r.top + 14, 14, 14)
        pygame.draw.rect(sup, col_ventana, win1)
        pygame.draw.rect(sup, col_ventana, win2)
        pygame.draw.rect(sup, (255, 255, 255), win1, 1)
        pygame.draw.rect(sup, (255, 255, 255), win2, 1)
        if self.entregado:
            GlowCache.blit(sup, win1.centerx, win1.centery, 18, (255, 200, 70), intensity=0.6)
            GlowCache.blit(sup, win2.centerx, win2.centery, 18, (255, 200, 70), intensity=0.6)

        # Tejado con capa de nieve superior
        pts_techo = [(r.left - 4, r.top), (r.centerx, r.top - 30), (r.right + 4, r.top)]
        pygame.draw.polygon(sup, (95, 48, 24), pts_techo)
        pygame.draw.lines(sup, (240, 248, 255), False, pts_techo, 4)

        if self.entregado:
            rx, ry = r.centerx - 10, r.bottom - 20
            pygame.draw.rect(sup, (220, 20, 20), (rx, ry, 20, 20), border_radius=2)
            pygame.draw.rect(sup, (255, 215, 0), (rx + 8, ry, 4, 20))
            pygame.draw.rect(sup, (255, 215, 0), (rx, ry + 8, 20, 4))


class XmasDelivery(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "OUTRO_3"
        self.jugador = None
        self.compañero = CompanionUI()
        self.casas = []
        self.obstaculos = []
        self.entregas = 0
        self.tiempo = 25.0
        self.timer_fase = 0.0
        self.ganado = False
        self.game_over = False
        self.timer_game_over = 0.0
        self.es_partida = True
        self.timer_victoria = 0.0
        self.fuente_ui = get_font(24, bold=True)
        self.fuente_over = get_font(40, bold=True)

        self.bg_surf = GradientCache.get_vertical(
            config.WIDTH, config.HEIGHT, (10, 22, 40), (20, 44, 66), vignette=True
        )
        self.nieve = FloatingParticles(count=35, mode="snow")
        self.gameover_overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        self.gameover_overlay.fill((200, 40, 50, 110))

    def startup(self):
        self.done = False
        self.next_state = "OUTRO_3"
        self.jugador = Player(100, config.HEIGHT // 2)
        self.jugador.velocidad = 350  # Trineo rápido
        self.casas = []
        self.obstaculos = []
        self.casas_entregadas = 0
        self.entregas = 0
        self.timer_fase = 0.0
        self.tiempo = 25.0
        self.ganado = False
        self.game_over = False
        self.timer_game_over = 0.0
        self.timer_victoria = 0.0
        self.logros_obtenidos = save_manager.cargar().get("secretos", [])

        # Generar casas aleatorias sin que se solapen mucho
        for _ in range(8):
            x = random.randint(200, config.WIDTH - 100)
            y = random.randint(100, config.HEIGHT - 100)
            intentos = 0
            while intentos < 100:
                colision = False
                for casa in self.casas:
                    if math.hypot(casa.rect.x - x, casa.rect.y - y) < 140:
                        colision = True
                        break
                if not colision:
                    break
                x = random.randint(200, config.WIDTH - 100)
                y = random.randint(100, config.HEIGHT - 100)
                intentos += 1

            self.casas.append(Casa(x, y))

        # Generar obstáculos pequeños en la ruta sin bloquear casas ni el inicio del jugador
        for i in range(10):
            for _ in range(80):
                ox = random.randint(175, config.WIDTH - 90)
                oy = random.randint(90, config.HEIGHT - 95)
                if math.hypot(ox - self.jugador.x, oy - self.jugador.y) < 110:
                    continue
                if any(math.hypot(ox - c.rect.centerx, oy - c.rect.centery) < 82 for c in self.casas):
                    continue
                if any(math.hypot(ox - o.x, oy - o.y) < 78 for o in self.obstaculos):
                    continue
                self.obstaculos.append(ObstaculoNavidad(ox, oy, variante=i % 2))
                break

        audio.reproducir_musica("assets/audio/fase3_nav.ogg", volumen=0.3)

    def manejar_eventos(self, evento):
        pass

    def actualizar(self, dt):
        self.compañero.actualizar(dt)
        self.nieve.update(dt)
        self.timer_fase += dt

        if self.ganado:
            self.timer_victoria += dt
            if self.timer_victoria > 1.5:
                save_manager.guardar(fase=4)
                self.next_state = "OUTRO_3"
                self.done = True
            return

        if getattr(self, "game_over", False):
            self.timer_game_over += dt
            if self.timer_game_over > 2.0:
                self.game_over = False
                self.startup()
            return

        self.tiempo -= dt
        if self.tiempo <= 0:
            if not getattr(self, "game_over", False):
                self.game_over = True
                self.timer_game_over = 0.0
                audio.reproducir("explosion")
                self.compañero.mostrar_mensaje("¡Uy, nos ganó el amanecer! Recargo el trineo rápido y vamos de nuevo.")
            return

        teclas = pygame.key.get_pressed()
        prev_x, prev_y = self.jugador.x, self.jugador.y
        self.jugador.actualizar(dt, teclas)
        new_x, new_y = self.jugador.x, self.jugador.y

        # Colisión deslizante por ejes separados contra los hitboxes ajustados de los obstáculos
        rect_x = pygame.Rect(int(new_x) - 8, int(prev_y) - 8, 16, 16)
        for obs in self.obstaculos:
            if rect_x.colliderect(obs.hitbox):
                new_x = prev_x
                break

        rect_y = pygame.Rect(int(new_x) - 8, int(new_y) - 8, 16, 16)
        for obs in self.obstaculos:
            if rect_y.colliderect(obs.hitbox):
                new_y = prev_y
                break

        self.jugador.x, self.jugador.y = new_x, new_y
        rect_jugador = pygame.Rect(int(self.jugador.x) - 10, int(self.jugador.y) - 10, 20, 20)

        for c in self.casas:
            if not c.entregado and rect_jugador.colliderect(c.rect):
                c.entregado = True
                self.entregas += 1
                audio.reproducir("anomalia")
                if self.entregas >= 8:
                    self.ganado = True
                    if self.tiempo >= 5.0 and "L3" not in self.logros_obtenidos:
                        save_manager.guardar(secreto="L3")
                        self.compañero.mostrar_mensaje(f"¡LOGRO: Santa Veloz! ¡Te sobraron {self.tiempo:.1f}s, eres rapidísima!")
                    else:
                        self.compañero.mostrar_mensaje("¡Todas las casas listas! Hacemos un gran equipo. Espera... ¿oíste eso?")

    def dibujar(self, superficie):
        superficie.blit(self.bg_surf, (0, 0))
        self.nieve.draw(superficie)

        for obs in self.obstaculos:
            obs.dibujar(superficie)
        for c in self.casas:
            c.dibujar(superficie, self.timer_fase)
        self.jugador.dibujar(superficie)

        hud_rect = pygame.Rect(14, 14, 360, 42)
        ProceduralUI.draw_panel(
            superficie, hud_rect,
            bg_color=(12, 24, 38, 215),
            border_color=(255, 80, 80) if self.tiempo < 5 else (255, 215, 0),
            cut=8,
            glow=False
        )
        txt = self.fuente_ui.render(
            f"Tiempo: {max(0, self.tiempo):.1f}s | Entregas: {self.entregas}/8",
            True, (255, 80, 80) if self.tiempo < 5 else (255, 255, 255)
        )
        superficie.blit(txt, (26, 21))

        if getattr(self, "game_over", False):
            superficie.blit(self.gameover_overlay, (0, 0))
            txt_over = self.fuente_over.render("TIEMPO AGOTADO", True, (255, 255, 255))
            superficie.blit(txt_over, txt_over.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2)))

        self.compañero.dibujar(superficie, self.jugador.y)
