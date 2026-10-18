import pygame
from utils.fonts import get_font
from utils.text_renderer import TypewriterText
from utils import audio
import config

class CompanionUI:
    def __init__(self):
        self.fuente = get_font(18, bold=True)
        self.escritor = None
        self.retrato = pygame.Surface((60, 60))
        self.retrato.fill((0, 255, 100)) 
        self.y_fija = config.HEIGHT - 95 # Se queda siempre abajo

    def mostrar_mensaje(self, texto, id_voz=None):
        audio.detener_sonido("tecla")
        max_ancho = config.WIDTH - 160
        self.escritor = TypewriterText(self.fuente, texto, (105, self.y_fija + 16), speed=0.04, max_width=max_ancho)
        if id_voz: audio.reproducir(id_voz, parar_anterior=True)

    def actualizar(self, dt):
        if self.escritor: self.escritor.actualizar(dt)

    def dibujar(self, superficie, jugador_y=0):
        # --- TRANSPARENCIA DINÁMICA ---
        alfa_fondo = 220
        alfa_borde = 255
        alfa_texto = 255
        
        # Si el jugador baja al territorio de la caja, esta se vuelve casi invisible
        if jugador_y > config.HEIGHT - 150:
            alfa_fondo = 40  # Caja fantasma
            alfa_borde = 50  # Borde fantasma
            alfa_texto = 100 # Texto legible pero transparente
            self.retrato.set_alpha(50)
        else:
            self.retrato.set_alpha(255)

        if self.escritor:
            self.escritor.pos = (105, self.y_fija + 16)

        # Fondos usando SRCALPHA para aceptar transparencias
        caja = pygame.Surface((config.WIDTH - 40, 80), pygame.SRCALPHA)
        caja.fill((10, 10, 15, alfa_fondo))
        superficie.blit(caja, (20, self.y_fija))
        
        borde = pygame.Surface((config.WIDTH - 40, 80), pygame.SRCALPHA)
        pygame.draw.rect(borde, (0, 255, 100, alfa_borde), (0, 0, config.WIDTH - 40, 80), 2)
        superficie.blit(borde, (20, self.y_fija))
        
        superficie.blit(self.retrato, (30, self.y_fija + 10))

        if self.escritor: 
            self.escritor.dibujar(superficie, alpha=alfa_texto)