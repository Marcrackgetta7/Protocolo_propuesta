import pygame
import os
import math
from states.base_state import BaseState
from entities.player import Player
from utils.text_renderer import TypewriterText
from utils import audio
import config

class Gallery(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "PROPOSAL" 
        self.jugador = None
        self.cam_x = 0
        # ¡Nivel mucho más largo para acomodar las 4 fotos y los 4 mensajes!
        self.largo_nivel = 7500 
        self.fuente_fotos = pygame.font.SysFont("consolas", 20)
        self.fuente_cartas = pygame.font.SysFont("consolas", 22, italic=True)
        self.tiempo_portal = 0.0

        # SECCIÓN 1: FOTOS (Imágenes con textos cortitos)
        self.recuerdos = [
            {"x": 600,  "ruta": "assets/img/foto1.jpg", "texto": "Nuestra primera locura...\n¿Te acuerdas?", "escritor": None},
            {"x": 2200, "ruta": "assets/img/foto2.jpg", "texto": "Tantas tazas de café para no dormir.", "escritor": None},
            {"x": 3800, "ruta": "assets/img/foto3.jpg", "texto": "Y aunque a veces soy un enano terco...", "escritor": None},
            {"x": 5400, "ruta": "assets/img/foto4.jpg", "texto": "Siempre has estado ahí para mí.", "escritor": None}
        ]
        
        # SECCIÓN 2: MENSAJES EXTENSOS (Cartas flotantes entre las fotos)
        # Puedes escribir párrafos largos usando \n para saltar de línea.
        self.mensajes_largos = [
            {"x": 1400, "texto": "A lo largo de todo este tiempo compartiendo juntos,\nme he dado cuenta de algo muy importante.\nAlgo que las líneas de código no pueden ocultar.", "escritor": None},
            
            {"x": 3000, "texto": "Más allá de las risas, los proyectos y las madrugadas,\nte has convertido en mi lugar seguro.\nLa persona con la que quiero compartirlo todo.", "escritor": None},
            
            {"x": 4600, "texto": "No quería que este juego fuera solo un proyecto escolar más.\nQuería que fuera algo inolvidable para los dos.\nUna prueba de lo mucho que me importas.", "escritor": None},
            
            {"x": 6200, "texto": "Así que, antes de que cruces este último umbral...\nQuiero que leas con atención la siguiente pantalla.\nRespira profundo.", "escritor": None}
        ]
        
        for rec in self.recuerdos:
            if os.path.exists(rec["ruta"]):
                img = pygame.image.load(rec["ruta"]).convert_alpha()
                rec["superficie"] = pygame.transform.scale(img, (300, 300))
            else:
                surf = pygame.Surface((300, 300))
                surf.fill((40, 40, 40))
                pygame.draw.rect(surf, (100, 100, 100), surf.get_rect(), 2)
                txt = self.fuente_fotos.render("FOTO FALTANTE", True, (100, 100, 100))
                surf.blit(txt, txt.get_rect(center=(150, 150)))
                rec["superficie"] = surf

    def startup(self):
        self.jugador = Player(100, config.HEIGHT // 2 + 50)
        self.cam_x = 0
        self.tiempo_portal = 0.0
        
        for rec in self.recuerdos: rec["escritor"] = None
        for msg in self.mensajes_largos: msg["escritor"] = None
            
        audio.reproducir_musica("assets/audio/bgm_final.ogg", volumen=0.5)

    def manejar_eventos(self, evento):
        pass 

    def actualizar(self, dt):
        self.tiempo_portal += dt
        teclas = pygame.key.get_pressed()
        
        vel = self.jugador.velocidad * dt
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]: self.jugador.x -= vel
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: self.jugador.x += vel
            
        if self.jugador.x < 50: self.jugador.x = 50
        
        # El portal está casi al final (7000px)
        if self.jugador.x > self.largo_nivel - 300:
            self.done = True

        self.cam_x = self.jugador.x - config.WIDTH // 2
        if self.cam_x < 0: self.cam_x = 0
        if self.cam_x > self.largo_nivel - config.WIDTH:
            self.cam_x = self.largo_nivel - config.WIDTH

        # Activar textos de fotos
        for rec in self.recuerdos:
            if abs(self.jugador.x - rec["x"]) < 400 and rec["escritor"] is None:
                rec["escritor"] = TypewriterText(self.fuente_fotos, rec["texto"], (rec["x"] - 150, config.HEIGHT // 2 + 100), speed=0.06)
            if rec["escritor"]: rec["escritor"].actualizar(dt)
                
        # Activar textos largos (Se activan cuando estás muy cerca para darle pausa dramática)
        for msg in self.mensajes_largos:
            if abs(self.jugador.x - msg["x"]) < 300 and msg["escritor"] is None:
                msg["escritor"] = TypewriterText(self.fuente_cartas, msg["texto"], (msg["x"] - 350, config.HEIGHT // 2 - 50), speed=0.05)
            if msg["escritor"]: msg["escritor"].actualizar(dt)

    def dibujar(self, superficie):
        superficie.fill((10, 10, 15)) 
        
        pygame.draw.line(superficie, (50, 50, 50), (0, config.HEIGHT // 2 + 80), (config.WIDTH, config.HEIGHT // 2 + 80), 2)

        # Dibujar Fotos
        for rec in self.recuerdos:
            pos_x_pantalla = rec["x"] - self.cam_x
            if -400 < pos_x_pantalla < config.WIDTH + 400:
                rect_img = rec["superficie"].get_rect(center=(pos_x_pantalla, config.HEIGHT // 2 - 100))
                superficie.blit(rec["superficie"], rect_img)
                pygame.draw.rect(superficie, config.COLOR_TEXT, rect_img, 3) 
                
                if rec["escritor"]:
                    rec["escritor"].pos = (pos_x_pantalla - 150, config.HEIGHT // 2 + 100)
                    rec["escritor"].dibujar(superficie)

        # Dibujar Mensajes Extensos
        for msg in self.mensajes_largos:
            pos_x_pantalla = msg["x"] - self.cam_x
            if -500 < pos_x_pantalla < config.WIDTH + 500:
                if msg["escritor"]:
                    msg["escritor"].pos = (pos_x_pantalla - 350, config.HEIGHT // 2 - 50)
                    msg["escritor"].dibujar(superficie)

        # Dibujar El Portal Final
        pos_portal = self.largo_nivel - 200 - self.cam_x
        if pos_portal < config.WIDTH + 200:
            radio = 80 + math.sin(self.tiempo_portal * 5) * 10
            pygame.draw.circle(superficie, config.COLOR_ENERGY, (int(pos_portal), config.HEIGHT // 2), int(radio))
            pygame.draw.circle(superficie, (255, 255, 255), (int(pos_portal), config.HEIGHT // 2), int(radio - 20))

        jugador_render_x = self.jugador.x - self.cam_x
        pygame.draw.rect(superficie, config.COLOR_TEXT, 
                         (jugador_render_x - 10, self.jugador.y - 10, 20, 20))