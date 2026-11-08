import math
import pygame
from utils.fonts import get_font
from states.base_state import BaseState
from entities.player import Player
from entities.monster import Monster
from utils.light_mask import LightMask
from utils.companion import CompanionUI
from utils.vfx import _CACHE, ScreenShake, GlowCache, BurstPool
from utils import audio
from utils import save_manager
import config

MAPA = [
    "111111111111111111111111",
    "1S0010002000001000000001",
    "101010111110101011111101",
    "102000000020101010000101",
    "101111101111100010110101",
    "100000100000111110100001",
    "111110111110000020101111",
    "100000000011111110100001",
    "101111111010000010111101",
    "101000002010111010000101",
    "101011111110101011110101",
    "1*F0000000001020000000E1",
    "111111111111111111111111",
]


class Maze(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "OUTRO_6"
        self.tam_celda = 40
        self.jugador = None
        self.monstruos = []
        self.mascara = LightMask()
        self.compañero = CompanionUI()
        self.shake = ScreenShake()
        self.paredes, self.paredes_falsas, self.cortafuegos = [], [], []
        self.salida, self.secreto_rect = None, None

        self.timer_hackeo = 0
        self.hackeando = False
        self.cortafuegos_actual = None

        self.cortafuegos_rotos = 0
        self.ganado, self.timer_victoria = False, 0.0
        self.game_over, self.timer_game_over = False, 0.0
        self.tiempo = 0.0
        self.fuente_over = get_font(40, bold=True)

        self.surf_temp = pygame.Surface((config.WIDTH, config.HEIGHT))
        self.wall_tile = self._get_circuit_wall(self.tam_celda)
        self.gameover_overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        self.gameover_overlay.fill((255, 0, 0, 100))
        self.bursts = BurstPool(capacity=40)

    @staticmethod
    def _get_circuit_wall(size):
        key = ("cyber_wall_tile", size)
        if key not in _CACHE:
            surf = pygame.Surface((size, size))
            surf.fill((22, 22, 28))
            pygame.draw.rect(surf, (45, 45, 58), (0, 0, size, size), 1)
            # Trazas de circuito impreso sutiles
            pygame.draw.line(surf, (36, 38, 52), (6, 6), (size - 12, 6), 1)
            pygame.draw.line(surf, (36, 38, 52), (size - 12, 6), (size - 6, 12), 1)
            pygame.draw.line(surf, (36, 38, 52), (10, size - 8), (size - 8, size - 8), 1)
            pygame.draw.circle(surf, (65, 30, 50), (6, 6), 2)
            pygame.draw.circle(surf, (65, 30, 50), (size - 8, size - 8), 2)
            _CACHE[key] = surf
        return _CACHE[key]

    def cleanup(self):
        """Elimina correctamente las instancias de enemigos y limpia listas y estados asociados."""
        for m in self.monstruos:
            if hasattr(m, "particulas"):
                m.particulas.clear()
        self.monstruos.clear()
        self.paredes.clear()
        self.paredes_falsas.clear()
        self.cortafuegos.clear()
        self.hackeando = False
        self.timer_hackeo = 0.0
        self.cortafuegos_actual = None
        self.game_over = False
        self.timer_game_over = 0.0
        self.ganado = False
        self.timer_victoria = 0.0
        self.cortafuegos_rotos = 0

    def startup(self):
        self.cleanup()
        self.done = False
        self.next_state = "OUTRO_6"
        self.paredes, self.paredes_falsas, self.cortafuegos, self.monstruos = [], [], [], []
        self.hackeando, self.ganado, self.timer_victoria = False, False, 0.0
        self.timer_hackeo = 0.0
        self.game_over, self.timer_game_over = False, 0.0
        self.cortafuegos_rotos = 0
        self.cortafuegos_actual = None
        self.secreto_rect = None
        self.tiempo = 0.0
        self.offset_x = (config.WIDTH - len(MAPA[0]) * self.tam_celda) // 2
        self.offset_y = (config.HEIGHT - len(MAPA) * self.tam_celda) // 2
        self.jugador = Player(self.offset_x + 100, self.offset_y + 100)  # Posición por defecto

        self.logros_obtenidos = save_manager.cargar().get("secretos", [])
        ya_tiene_secreto = "Código Muerto" in self.logros_obtenidos
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
                elif char == "2":
                    self.cortafuegos.append(rect)
                elif char == "E":
                    self.salida = rect
                elif char == "S":
                    self.jugador = Player(x + self.tam_celda // 2, y + self.tam_celda // 2)
                elif char == "*" and not ya_tiene_secreto:
                    self.secreto_rect = rect

        self.fase_oscura = True
        self.es_partida = True

        self.monstruos = [
            Monster(self.offset_x + 500, self.offset_y + 200)
        ]

        self.compañero.mostrar_mensaje("No te asustes por la oscuridad. Toca las terminales verdes y te daré luz.", id_voz="v_f2_in")
        audio.reproducir_musica("assets/audio/Fase2_dark.ogg", volumen=0.3)

    def manejar_eventos(self, evento):
        pass

    def actualizar(self, dt):
        self.tiempo += dt
        self.shake.actualizar(dt)
        self.compañero.actualizar(dt)
        self.bursts.update(dt)

        if getattr(self, "game_over", False):
            self.timer_game_over += dt
            if self.timer_game_over > 2.0:
                self.game_over = False
                self.startup()
            return

        if self.ganado:
            self.timer_victoria += dt
            if self.timer_victoria > 1.5:
                save_manager.guardar(fase=7)
                self.next_state = "OUTRO_6"
                self.done = True
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
        for p in self.paredes + self.cortafuegos:
            if rect_jugador.colliderect(p):
                self.jugador.x -= dx * vel
                break

        self.jugador.y += dy * vel
        rect_jugador = pygame.Rect(int(self.jugador.x) - 10, int(self.jugador.y) - 10, 20, 20)
        for p in self.paredes + self.cortafuegos:
            if rect_jugador.colliderect(p):
                self.jugador.y -= dy * vel
                break
        rect_jugador = pygame.Rect(int(self.jugador.x) - 10, int(self.jugador.y) - 10, 20, 20)

        for m in self.monstruos:
            m.actualizar(dt, self.jugador.x, self.jugador.y)

        if self.secreto_rect and rect_jugador.colliderect(self.secreto_rect):
            save_manager.guardar(secreto="Código Muerto")
            self.secreto_rect = None
            self.compañero.mostrar_mensaje("¡SECRETO: Código Muerto! Hasta en plena crisis encuentras rincones ocultos.")

        if not self.hackeando:
            for cf in self.cortafuegos:
                if math.hypot(self.jugador.x - cf.centerx, self.jugador.y - cf.centery) < 45:
                    self.hackeando, self.cortafuegos_actual, self.timer_hackeo = True, cf, 0.8
                    self.compañero.mostrar_mensaje("¡Es un cortafuegos! Quédate cerquita un segundo mientras lo elimino...")
                    break
        else:
            dist_cancel = math.hypot(self.jugador.x - self.cortafuegos_actual.centerx, self.jugador.y - self.cortafuegos_actual.centery)
            if dist_cancel > 60:
                self.hackeando = False
                self.compañero.mostrar_mensaje("¡Ey, se cortó la señal! Vuelve a acercarte al muro para terminar.")
            else:
                self.timer_hackeo -= dt
                if self.timer_hackeo <= 0:
                    self.shake.iniciar(8, 0.2)
                    audio.reproducir("explosion")
                    self.bursts.emit(
                        self.cortafuegos_actual.centerx, self.cortafuegos_actual.centery,
                        count=18, colors=[config.COLOR_ENERGY, (0, 255, 140), (255, 255, 255)], heart_chance=0.0
                    )
                    if self.cortafuegos_actual in self.cortafuegos:
                        self.cortafuegos.remove(self.cortafuegos_actual)
                    self.cortafuegos_actual = None
                    self.hackeando = False
                    self.cortafuegos_rotos += 1
                    self.compañero.mostrar_mensaje(f"¡Abierto! ({self.cortafuegos_rotos}/3) ¡Corre, el ruido atrajo a un Limpiador!")
                    self.monstruos.append(Monster(self.offset_x + 880, self.offset_y + 440))

        for m in self.monstruos:
            if math.hypot(self.jugador.x - m.x, self.jugador.y - m.y) < (self.jugador.radio_nucleo + m.radio):
                if not getattr(self, "game_over", False):
                    self.game_over = True
                    self.timer_game_over = 0.0
                    self.shake.iniciar(15, 0.4)
                    self.compañero.mostrar_mensaje("¡No! ¡Te alcanzó! Espera, rebobino el código para salvarte... ¡Listo!")
                break

        if rect_jugador.colliderect(self.salida):
            if not self.ganado:
                self.ganado = True
                self.timer_victoria = 0.0
                for m in self.monstruos:
                    if hasattr(m, "particulas"):
                        m.particulas.clear()
                self.monstruos.clear()
                if self.cortafuegos_rotos >= 3 and "L6" not in self.logros_obtenidos:
                    save_manager.guardar(secreto="L6")
                    self.compañero.mostrar_mensaje("¡LOGRO: Fuerza Bruta! ¿Para qué rodear si podíamos romper todo, verdad?")
                else:
                    self.compañero.mostrar_mensaje("¡Salimos de ese laberinto! Respira... ya estamos cerca del final.")

    def dibujar(self, superficie):
        self.surf_temp.fill((5, 5, 8))
        pulso = 0.7 + 0.3 * math.sin(self.tiempo * 6.0)

        for p in self.paredes + self.paredes_falsas:
            self.surf_temp.blit(self.wall_tile, p.topleft)

        for c in self.cortafuegos:
            GlowCache.blit(self.surf_temp, c.centerx, c.centery, int(30 * pulso), config.COLOR_ENERGY, intensity=0.55)
            pygame.draw.rect(self.surf_temp, (45, 10, 25), c)
            pygame.draw.rect(self.surf_temp, config.COLOR_ENERGY, c, 2)
            pygame.draw.rect(self.surf_temp, (255, 150, 200), c.inflate(-14, -14), 1)

        # Portal de salida
        GlowCache.blit(self.surf_temp, self.salida.centerx, self.salida.centery, 32, (200, 230, 255), intensity=0.6)
        pygame.draw.rect(self.surf_temp, (200, 220, 240), self.salida, border_radius=4)
        pygame.draw.rect(self.surf_temp, (255, 255, 255), self.salida, 2, border_radius=4)

        if self.secreto_rect:
            GlowCache.blit(self.surf_temp, self.secreto_rect.centerx, self.secreto_rect.centery, 28, config.COLOR_DANGER, intensity=0.65)
            pygame.draw.rect(self.surf_temp, config.COLOR_DANGER, self.secreto_rect)
            pygame.draw.rect(self.surf_temp, config.COLOR_TEXT, self.secreto_rect, 1)

        for m in self.monstruos:
            m.dibujar(self.surf_temp)
        self.jugador.dibujar(self.surf_temp)
        self.bursts.draw(self.surf_temp)

        # Anillo de progreso circular de hackeo y enlace láser hacia el cortafuegos
        if self.hackeando and self.cortafuegos_actual:
            progreso = max(0.0, min(1.0, 1.0 - (self.timer_hackeo / 0.8)))
            jx, jy = int(self.jugador.x), int(self.jugador.y)
            pygame.draw.line(
                self.surf_temp, (0, 255, 140),
                (jx, jy), self.cortafuegos_actual.center, 2
            )
            arc_rect = pygame.Rect(jx - 22, jy - 22, 44, 44)
            pygame.draw.arc(self.surf_temp, (0, 255, 140), arc_rect, 0, progreso * math.tau, 3)

        ox, oy = self.shake.obtener_offset()
        superficie.blit(self.surf_temp, (ox, oy))
        self.mascara.dibujar(superficie, (self.jugador.x, self.jugador.y))

        if getattr(self, "game_over", False):
            superficie.blit(self.gameover_overlay, (0, 0))
            txt = self.fuente_over.render("SISTEMA COMPROMETIDO", True, (255, 255, 255))
            superficie.blit(txt, txt.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2)))

        self.compañero.dibujar(superficie, self.jugador.y)
