import os
import math
import pygame
from utils.fonts import get_font
from states.base_state import BaseState
from entities.player import Player
from utils.text_renderer import TypewriterText
from utils import audio
from utils.vfx import (
    GlowCache,
    GradientCache,
    HeartRenderer,
    FloatingParticles,
    TrailRenderer,
    ProceduralUI,
)
import config


class Gallery(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "PROPOSAL"
        self.jugador = None
        self.cam_x = 0
        # Nivel extendido a 11000 píxeles para acomodar 5 fotos y 7 textos
        self.largo_nivel = 11000
        self.fuente_fotos = get_font(20)
        self.fuente_cartas = get_font(22, italic=True)
        self.tiempo_portal = 0.0

        # Pre-cálculo de fondo, paralaje y estela
        self.bg_surf = GradientCache.get_vertical(
            config.WIDTH, config.HEIGHT, (8, 8, 18), (22, 10, 26), vignette=True
        )
        self.particulas_fondo = FloatingParticles(count=36, mode="romantic")
        self.estela_jugador = TrailRenderer(max_points=14)
        self.estrellas_lejanas = [
            ((i * 197) % config.WIDTH, (i * 89) % (config.HEIGHT // 2 + 40), (i % 3) + 1)
            for i in range(65)
        ]

        # SECCIÓN 1: FOTOS (5 Fotos separadas cada 1600 píxeles)
        self.recuerdos = [
            {"x": 600,  "ruta": "assets/img/img1.png", "texto": "Nuestra primera locura...\n¿Te acuerdas?", "escritor": None},
            {"x": 2200, "ruta": "assets/img/img2.png", "texto": "Tantas tazas de café para no dormir.", "escritor": None},
            {"x": 3800, "ruta": "assets/img/img3.png", "texto": "Y aunque a veces soy un enano terco...", "escritor": None},
            {"x": 5400, "ruta": "assets/img/img4.png", "texto": "Siempre has estado ahí para mí.", "escritor": None},
            {"x": 7000, "ruta": "assets/img/img5.png", "texto": "Cada momento a tu lado es especial.", "escritor": None}
        ]

        # SECCIÓN 2: MENSAJES EXTENSOS (Alternan con las fotos y al final hay 3 seguidos)
        self.mensajes_largos = [
            {"x": 1400, "texto": "A lo largo de todo este tiempo compartiendo juntos,\nme he dado cuenta de algo muy importante.\nAlgo que las líneas de código no pueden ocultar.", "escritor": None},
            {"x": 3000, "texto": "Más allá de las risas, los proyectos y las madrugadas,\nte has convertido en mi lugar seguro.", "escritor": None},
            {"x": 4600, "texto": "No quería que este juego fuera solo un proyecto más.\nQuería que fuera algo inolvidable para los dos.", "escritor": None},
            {"x": 6200, "texto": "Una pequeña prueba de todo lo que significas para mí.", "escritor": None},
            {"x": 7800, "texto": "[ESPACIO PARA EXPRESARTE 1]\nAquí puedes escribir sobre cómo te sentiste al conocerla,\no algún detalle muy específico que solo ustedes entiendan.", "escritor": None},
            {"x": 8600, "texto": "[ESPACIO PARA EXPRESARTE 2]\nAquí puedes hablar sobre lo que admiras de ella,\nsu forma de ser, o cómo te hace sentir día a día.", "escritor": None},
            {"x": 9400, "texto": "Así que, antes de que cruces este último umbral...\nQuiero que leas con atención la siguiente pantalla.\nRespira profundo.", "escritor": None}
        ]

        # Cargar imágenes de forma segura
        for rec in self.recuerdos:
            if os.path.exists(rec["ruta"]):
                img = pygame.image.load(rec["ruta"]).convert_alpha()
                rec["superficie"] = pygame.transform.scale(img, (300, 300))
            else:
                surf = pygame.Surface((300, 300))
                surf.fill((25, 18, 32))
                pygame.draw.rect(surf, config.COLOR_ENERGY, surf.get_rect(), 2)
                HeartRenderer.draw(surf, 150, 125, scale=1.4, color=config.COLOR_ENERGY, alpha=160, glow=True)
                txt = self.fuente_fotos.render("RECUERDO", True, config.COLOR_TEXT)
                surf.blit(txt, txt.get_rect(center=(150, 215)))
                rec["superficie"] = surf

    def startup(self):
        self.jugador = Player(100, config.HEIGHT // 2 + 50)
        self.cam_x = 0
        self.tiempo_portal = 0.0
        self.estela_jugador.clear()

        for rec in self.recuerdos:
            rec["escritor"] = None
        for msg in self.mensajes_largos:
            msg["escritor"] = None

        audio.reproducir_musica("assets/audio/Final_pasillo.ogg", volumen=0.5)

    def manejar_eventos(self, evento):
        pass

    def actualizar(self, dt):
        self.tiempo_portal += dt
        self.particulas_fondo.update(dt)
        teclas = pygame.key.get_pressed()

        vel = self.jugador.velocidad * dt
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.jugador.x -= vel
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.jugador.x += vel

        if self.jugador.x < 50:
            self.jugador.x = 50

        self.estela_jugador.add(self.jugador.x, self.jugador.y)

        # El portal está cerca del final (10600px)
        if self.jugador.x > self.largo_nivel - 300:
            self.done = True

        self.cam_x = self.jugador.x - config.WIDTH // 2
        if self.cam_x < 0:
            self.cam_x = 0
        if self.cam_x > self.largo_nivel - config.WIDTH:
            self.cam_x = self.largo_nivel - config.WIDTH

        # Activar textos de fotos
        for rec in self.recuerdos:
            if abs(self.jugador.x - rec["x"]) < 400 and rec["escritor"] is None:
                rec["escritor"] = TypewriterText(
                    self.fuente_fotos, rec["texto"], (rec["x"] - 150, config.HEIGHT // 2 + 100), speed=0.06
                )
            if rec["escritor"]:
                rec["escritor"].actualizar(dt)

        # Activar textos largos
        for msg in self.mensajes_largos:
            if abs(self.jugador.x - msg["x"]) < 300 and msg["escritor"] is None:
                msg["escritor"] = TypewriterText(
                    self.fuente_cartas, msg["texto"], (msg["x"] - 350, config.HEIGHT // 2 - 50), speed=0.05
                )
            if msg["escritor"]:
                msg["escritor"].actualizar(dt)

    def dibujar(self, superficie):
        superficie.blit(self.bg_surf, (0, 0))

        # Capa 1: Estrellas con paralaje lento (0.15x)
        for sx, sy, sz in self.estrellas_lejanas:
            px = int((sx - self.cam_x * 0.15) % config.WIDTH)
            brillo = 150 + int(95 * math.sin(self.tiempo_portal * 2.0 + sx))
            pygame.draw.circle(superficie, (brillo, brillo, 255), (px, sy), sz)

        # Capa 2: Pilares de luz ambientales en paralaje medio (0.45x)
        piso_y = config.HEIGHT // 2 + 80
        for i in range(16):
            pilar_x = int(((i * 320) - self.cam_x * 0.45) % (config.WIDTH + 320)) - 160
            pygame.draw.line(superficie, (35, 18, 42), (pilar_x, 0), (pilar_x, piso_y), 2)
            GlowCache.blit(superficie, pilar_x, piso_y, 28, config.COLOR_ENERGY, intensity=0.22)

        # Capa 3: Partículas flotantes con paralaje (0.6x)
        self.particulas_fondo.draw(superficie, cam_x=self.cam_x, parallax=0.6)

        # Piso con horizonte brillante y líneas de perspectiva
        GlowCache.blit(superficie, config.WIDTH // 2, piso_y, 180, config.COLOR_ENERGY, intensity=0.15)
        pygame.draw.line(superficie, config.COLOR_ENERGY, (0, piso_y), (config.WIDTH, piso_y), 2)
        pygame.draw.line(superficie, (255, 180, 210), (0, piso_y + 3), (config.WIDTH, piso_y + 3), 1)

        # Dibujar Fotos con marco luminoso y foco cenital
        for rec in self.recuerdos:
            pos_x_pantalla = rec["x"] - self.cam_x
            if -400 < pos_x_pantalla < config.WIDTH + 400:
                flote = math.sin(self.tiempo_portal * 2.2 + rec["x"] * 0.01) * 5
                cy_foto = int(config.HEIGHT // 2 - 100 + flote)
                rect_img = rec["superficie"].get_rect(center=(int(pos_x_pantalla), cy_foto))

                # Halo detrás del marco
                GlowCache.blit(superficie, rect_img.centerx, rect_img.centery, 195, config.COLOR_ENERGY, intensity=0.35)
                marco_ext = rect_img.inflate(16, 16)
                ProceduralUI.draw_panel(
                    superficie, marco_ext,
                    bg_color=(18, 10, 26, 220),
                    border_color=config.COLOR_ENERGY,
                    cut=10,
                    glow=False
                )
                superficie.blit(rec["superficie"], rect_img)
                pygame.draw.rect(superficie, config.COLOR_TEXT, rect_img, 2)

                if rec["escritor"]:
                    caja_txt = pygame.Rect(int(pos_x_pantalla) - 180, config.HEIGHT // 2 + 90, 360, 72)
                    ProceduralUI.draw_panel(
                        superficie, caja_txt,
                        bg_color=(12, 8, 20, 190),
                        border_color=(255, 130, 180),
                        cut=8,
                        glow=False
                    )
                    rec["escritor"].pos = (int(pos_x_pantalla) - 150, config.HEIGHT // 2 + 100)
                    rec["escritor"].dibujar(superficie)

        # Dibujar Mensajes Extensos en paneles flotantes
        for msg in self.mensajes_largos:
            pos_x_pantalla = msg["x"] - self.cam_x
            if -500 < pos_x_pantalla < config.WIDTH + 500:
                if msg["escritor"]:
                    flote_msg = int(math.sin(self.tiempo_portal * 2.0 + msg["x"] * 0.01) * 4)
                    panel_msg = pygame.Rect(int(pos_x_pantalla) - 380, config.HEIGHT // 2 - 80 + flote_msg, 760, 135)
                    ProceduralUI.draw_panel(
                        superficie, panel_msg,
                        bg_color=(16, 10, 26, 205),
                        border_color=config.COLOR_ENERGY,
                        cut=14,
                        glow=True
                    )
                    HeartRenderer.draw(
                        superficie, panel_msg.centerx, panel_msg.top - 14,
                        scale=0.35, color=config.COLOR_ENERGY, alpha=210, glow=True
                    )
                    msg["escritor"].pos = (int(pos_x_pantalla) - 350, config.HEIGHT // 2 - 50 + flote_msg)
                    msg["escritor"].dibujar(superficie)

        # Dibujar El Portal Final (Vórtice multicapa)
        pos_portal = self.largo_nivel - 200 - self.cam_x
        if pos_portal < config.WIDTH + 240:
            px, py = int(pos_portal), config.HEIGHT // 2
            radio = 80 + math.sin(self.tiempo_portal * 5) * 10
            GlowCache.blit(superficie, px, py, int(radio * 2.1), config.COLOR_ENERGY, intensity=0.85)

            # Anillos de energía giratorios
            for i in range(3):
                r_anillo = int(radio - i * 16)
                pygame.draw.circle(
                    superficie,
                    config.COLOR_ENERGY if i % 2 == 0 else (255, 160, 210),
                    (px, py),
                    max(10, r_anillo),
                    3
                )
            pygame.draw.circle(superficie, (255, 255, 255), (px, py), int(radio - 28))
            HeartRenderer.draw(
                superficie, px, py,
                scale=1.1 + 0.15 * math.sin(self.tiempo_portal * 6.0),
                color=config.COLOR_ENERGY,
                alpha=240,
                glow=True
            )

        # Dibujar estela y jugador desplazado por la cámara
        for i, (tx, ty) in enumerate(self.estela_jugador.points):
            ratio = (i + 1) / max(1, len(self.estela_jugador.points))
            GlowCache.blit(superficie, tx - self.cam_x, ty, int(12 * ratio), config.COLOR_ENERGY, intensity=0.35 * ratio)

        jugador_render_x = int(self.jugador.x - self.cam_x)
        jugador_render_y = int(self.jugador.y)
        GlowCache.blit(superficie, jugador_render_x, jugador_render_y, 24, (255, 200, 230), intensity=0.7)
        pygame.draw.circle(superficie, config.COLOR_ENERGY, (jugador_render_x, jugador_render_y), 9)
        pygame.draw.circle(superficie, config.COLOR_TEXT, (jugador_render_x, jugador_render_y), 5)
