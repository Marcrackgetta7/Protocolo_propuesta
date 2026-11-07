import math
import pygame
from utils.fonts import get_font
from states.base_state import BaseState
from entities.player import Player
from utils.companion import CompanionUI
from utils import audio
from utils import save_manager
from utils.vfx import _CACHE, ScreenShake, GlowCache, GradientCache, ProceduralUI
import config

MAPA = [
    "111111111111111111111111",
    "1S0010000000001000000001",
    "101010111110101011111101",
    "100000000000101010000C01",
    "101111101111100010110101",
    "10000C100000111110100001",
    "111110111110000000101111",
    "100000000011111110100001",
    "101111111010000010111101",
    "10C000000010111010000C01",
    "101011111110101011110101",
    "10000000000010F*100000E1",
    "111111111111111111111111",
]


class Snowman:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.radio = 12
        self.velocidad = 50.0

    def actualizar(self, dt, jugador_x, jugador_y):
        dx = jugador_x - self.x
        dy = jugador_y - self.y
        distancia = math.hypot(dx, dy)
        if distancia > 0:
            self.x += (dx / distancia) * self.velocidad * dt
            self.y += (dy / distancia) * self.velocidad * dt

    def dibujar(self, sup, ox=0, oy=0):
        cx, cy = int(self.x) + ox, int(self.y) + oy
        GlowCache.blit(sup, cx, cy - 4, 28, (130, 200, 255), intensity=0.5)
        # Cuerpo y cabeza con sombreado
        pygame.draw.circle(sup, (210, 230, 250), (cx, cy), self.radio)
        pygame.draw.circle(sup, (255, 255, 255), (cx - 2, cy - 2), self.radio - 2)
        pygame.draw.circle(sup, (210, 230, 250), (cx, cy - 12), self.radio - 4)
        pygame.draw.circle(sup, (255, 255, 255), (cx - 1, cy - 13), self.radio - 5)
        # Bufanda roja
        pygame.draw.rect(sup, (220, 30, 40), (cx - 7, cy - 6, 14, 4), border_radius=2)
        pygame.draw.rect(sup, (220, 30, 40), (cx + 2, cy - 5, 4, 9), border_radius=1)
        # Ojos y nariz de zanahoria
        pygame.draw.circle(sup, (20, 20, 30), (cx - 3, cy - 14), 1)
        pygame.draw.circle(sup, (20, 20, 30), (cx + 3, cy - 14), 1)
        pygame.draw.polygon(sup, (255, 140, 20), [(cx, cy - 12), (cx + 6, cy - 11), (cx, cy - 10)])


class XmasMaze(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "OUTRO_2"
        self.es_partida = True
        self.tam_celda = 40
        self.jugador = None
        self.compañero = CompanionUI()
        self.shake = ScreenShake()
        self.paredes = []
        self.paredes_falsas = []
        self.esferas = []
        self.snowmen = []
        self.salida = None
        self.secreto_rect = None
        self.esferas_recogidas = 0
        self.tiempo_jugado = 0.0
        self.tiempo_restante = 60.0
        self.ganado = False
        self.timer_victoria = 0.0
        self.game_over = False
        self.timer_game_over = 0.0
        self.fuente_ui = get_font(24, bold=True)
        self.fuente_over = get_font(40, bold=True)

        self.surf_temp = pygame.Surface((config.WIDTH, config.HEIGHT))
        self.bg_surf = GradientCache.get_vertical(
            config.WIDTH, config.HEIGHT, (14, 30, 48), (22, 46, 68), vignette=True
        )
        self.ice_tile = self._get_ice_tile(self.tam_celda)
        self.gameover_overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        self.gameover_overlay.fill((200, 40, 60, 110))

    @staticmethod
    def _get_ice_tile(size):
        key = ("xmas_ice_tile", size)
        if key not in _CACHE:
            surf = pygame.Surface((size, size))
            surf.fill((125, 180, 235))
            # Bisel superior/izquierdo claro y borde inferior/derecho profundo
            pygame.draw.polygon(surf, (195, 230, 255), [(0, 0), (size, 0), (size - 4, 4), (4, 4), (4, size - 4), (0, size)])
            pygame.draw.polygon(surf, (80, 130, 190), [(size, 0), (size, size), (0, size), (4, size - 4), (size - 4, size - 4), (size - 4, 4)])
            # Reflejo diagonal cristalino
            pygame.draw.line(surf, (225, 245, 255), (6, size - 8), (size - 8, 6), 2)
            pygame.draw.rect(surf, (210, 240, 255), (0, 0, size, size), 1)
            _CACHE[key] = surf
        return _CACHE[key]

    def cleanup(self):
        self.snowmen.clear()
        self.esferas.clear()
        self.paredes.clear()
        self.paredes_falsas.clear()
        self.ganado = False
        self.timer_victoria = 0.0

    def startup(self):
        self.cleanup()
        self.done = False
        self.next_state = "OUTRO_2"
        self.paredes, self.paredes_falsas, self.esferas, self.snowmen = [], [], [], []
        self.esferas_recogidas, self.tiempo_jugado = 0, 0.0
        self.tiempo_restante = 60.0
        self.secreto_rect = None
        self.ganado, self.timer_victoria = False, 0.0
        self.game_over, self.timer_game_over = False, 0.0

        self.logros_obtenidos = save_manager.cargar().get("secretos", [])
        ya_tiene_secreto = "Estrella Helada" in self.logros_obtenidos

        self.offset_x = (config.WIDTH - len(MAPA[0]) * self.tam_celda) // 2
        self.offset_y = (config.HEIGHT - len(MAPA) * self.tam_celda) // 2
        for fila in range(len(MAPA)):
            for col in range(len(MAPA[fila])):
                char = MAPA[fila][col]
                x = self.offset_x + col * self.tam_celda
                y = self.offset_y + fila * self.tam_celda
                rect = pygame.Rect(x, y, self.tam_celda, self.tam_celda)
                if char == "1":
                    self.paredes.append(rect)
                elif char == "F":
                    self.paredes_falsas.append(rect)
                elif char == "*" and not ya_tiene_secreto:
                    self.secreto_rect = rect
                elif char == "C":
                    self.esferas.append(rect)
                elif char == "S":
                    self.jugador = Player(x + self.tam_celda // 2, y + self.tam_celda // 2)
                elif char == "E":
                    self.salida = rect

        self.snowmen = [
            Snowman(self.offset_x + 800, self.offset_y + 200),
            Snowman(self.offset_x + 300, self.offset_y + 400)
        ]

        self.compañero.mostrar_mensaje("Bosque Nevado. Encuentra las 4 esferas para abrir el camino.")
        audio.reproducir_musica("assets/audio/Fase2_nav.ogg", volumen=0.4)

    def manejar_eventos(self, evento):
        pass

    def actualizar(self, dt):
        self.shake.actualizar(dt)
        self.compañero.actualizar(dt)

        if getattr(self, "game_over", False):
            self.timer_game_over += dt
            if self.timer_game_over > 2.0:
                self.game_over = False
                self.startup()
            return

        if self.ganado:
            self.timer_victoria += dt
            if self.timer_victoria > 1.5:
                save_manager.guardar(fase=3)
                self.next_state = "OUTRO_2"
                self.done = True
            return

        self.tiempo_jugado += dt
        self.tiempo_restante -= dt

        if self.tiempo_restante <= 0:
            self.tiempo_restante = 0
            if not getattr(self, "game_over", False):
                self.game_over = True
                self.timer_game_over = 0.0
                audio.reproducir("explosion")
                self.compañero.mostrar_mensaje("¡Se acabó el tiempo! Has quedado congelado.")
            return

        teclas = pygame.key.get_pressed()
        vel = self.jugador.velocidad * dt

        dx = 0
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            dx -= 1
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            dx += 1
        dy = 0
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            dy -= 1
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            dy += 1

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        self.jugador.x += dx * vel
        rect_jugador = pygame.Rect(int(self.jugador.x) - 10, int(self.jugador.y) - 10, 20, 20)
        for p in self.paredes:
            if rect_jugador.colliderect(p):
                self.jugador.x -= dx * vel
                break

        self.jugador.y += dy * vel
        rect_jugador = pygame.Rect(int(self.jugador.x) - 10, int(self.jugador.y) - 10, 20, 20)
        for p in self.paredes:
            if rect_jugador.colliderect(p):
                self.jugador.y -= dy * vel
                break
        rect_jugador = pygame.Rect(int(self.jugador.x) - 10, int(self.jugador.y) - 10, 20, 20)

        for e in self.esferas[:]:
            if rect_jugador.colliderect(e):
                self.esferas.remove(e)
                self.esferas_recogidas += 1
                audio.reproducir("anomalia")
                if self.esferas_recogidas == 4:
                    self.compañero.mostrar_mensaje("¡Todas las esferas listas! Corre al portal verde.")

        if self.secreto_rect and rect_jugador.colliderect(self.secreto_rect):
            save_manager.guardar(secreto="Estrella Helada")
            self.secreto_rect = None
            self.compañero.mostrar_mensaje("¡SECRETO DESCUBIERTO: Estrella Helada!")

        for sm in self.snowmen:
            sm.actualizar(dt, self.jugador.x, self.jugador.y)
            if math.hypot(self.jugador.x - sm.x, self.jugador.y - sm.y) < (self.jugador.radio_nucleo + sm.radio):
                if not getattr(self, "game_over", False):
                    self.game_over = True
                    self.timer_game_over = 0.0
                    self.shake.iniciar(10, 0.4)
                    audio.reproducir("explosion")
                    self.compañero.mostrar_mensaje("¡Te atrapó un muñeco de nieve!")

        if self.esferas_recogidas >= 4 and rect_jugador.colliderect(self.salida):
            if not self.ganado:
                self.ganado = True
                self.timer_victoria = 0.0
                self.snowmen.clear()
                if self.tiempo_jugado < 15.0 and "L2" not in self.logros_obtenidos:
                    save_manager.guardar(secreto="L2")
                    self.compañero.mostrar_mensaje("¡LOGRO DESBLOQUEADO: Velocista Nevado (<15s)!")
                else:
                    self.compañero.mostrar_mensaje("¡Nivel Completado! Avanzando...")

    def dibujar(self, superficie):
        self.surf_temp.blit(self.bg_surf, (0, 0))
        pulso = 1.0 + 0.15 * math.sin(self.tiempo_jugado * 5.0)

        for p in self.paredes + self.paredes_falsas:
            self.surf_temp.blit(self.ice_tile, p.topleft)

        for e in self.esferas:
            cx, cy = e.center
            GlowCache.blit(self.surf_temp, cx, cy, int(24 * pulso), (255, 215, 0), intensity=0.65)
            pygame.draw.circle(self.surf_temp, (255, 200, 0), (cx, cy), 10)
            pygame.draw.circle(self.surf_temp, (255, 250, 200), (cx - 3, cy - 3), 3)

        if self.secreto_rect:
            scx, scy = self.secreto_rect.center
            GlowCache.blit(self.surf_temp, scx, scy, int(30 * pulso), (255, 215, 0), intensity=0.75)
            pygame.draw.rect(self.surf_temp, (255, 215, 0), self.secreto_rect, border_radius=6)
            pygame.draw.rect(self.surf_temp, (255, 255, 255), self.secreto_rect, 2, border_radius=6)

        color_salida = (50, 255, 90) if self.esferas_recogidas >= 4 else (255, 60, 60)
        GlowCache.blit(self.surf_temp, self.salida.centerx, self.salida.centery, 34, color_salida, intensity=0.6)
        pygame.draw.rect(self.surf_temp, color_salida, self.salida, border_radius=6)
        pygame.draw.rect(self.surf_temp, (255, 255, 255), self.salida, 2, border_radius=6)

        for sm in self.snowmen:
            sm.dibujar(self.surf_temp)
        self.jugador.dibujar(self.surf_temp)

        hud_rect = pygame.Rect(14, 14, 210, 42)
        ProceduralUI.draw_panel(
            self.surf_temp, hud_rect,
            bg_color=(12, 24, 38, 215),
            border_color=(160, 220, 255),
            cut=8,
            glow=False
        )
        txt_tiempo = self.fuente_ui.render(f"Tiempo: {max(0, self.tiempo_restante):.1f}s", True, (255, 255, 255))
        self.surf_temp.blit(txt_tiempo, (26, 21))

        ox, oy = self.shake.obtener_offset()
        superficie.blit(self.surf_temp, (ox, oy))

        if getattr(self, "game_over", False):
            superficie.blit(self.gameover_overlay, (0, 0))
            txt_over = self.fuente_over.render("CONGELADO", True, (255, 255, 255))
            superficie.blit(txt_over, txt_over.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2)))

        self.compañero.dibujar(superficie, self.jugador.y)
