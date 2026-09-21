import pygame
from utils.text_renderer import TypewriterText
from utils import audio
import config

class CompanionUI:
    def __init__(self):
        self.fuente = pygame.font.SysFont("consolas", 18, bold=True)
        self.escritor = None
        self.retrato = pygame.Surface((60, 60))
        self.retrato.fill((0, 255, 100)) 
        self.y_fija = config.HEIGHT - 100 # Se queda siempre abajo

    def mostrar_mensaje(self, texto, id_voz=None):
        audio.detener_sonido("tecla")
        self.escritor = TypewriterText(self.fuente, texto, (110, self.y_fija + 20), speed=0.04)
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
            self.escritor.pos = (110, self.y_fija + 20)

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