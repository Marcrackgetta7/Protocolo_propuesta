import pygame
from utils.text_renderer import TypewriterText
from utils import audio # Importamos el gestor de audio
import config

class CompanionUI:
    def __init__(self):
        self.fuente_nombre = pygame.font.SysFont("consolas", 20, bold=True)
        self.fuente_texto = pygame.font.SysFont("consolas", 20)
        self.color_nombre = (0, 255, 100) 
        self.color_fondo = (10, 10, 10, 220) 
        self.rect_fondo = pygame.Rect(0, config.HEIGHT - 80, config.WIDTH, 80)
        
        self.activo = False
        self.escritor = None
        self.nombre = "[MARCELO]:"

    def mostrar_mensaje(self, texto, id_voz=None):
        self.activo = True
        self.escritor = TypewriterText(self.fuente_texto, texto, (150, config.HEIGHT - 50), speed=0.01)
        
        # Lógica de audio para el diálogo
        if id_voz:
            audio.reproducir(id_voz) # Si le pasas el ID de tu grabación, suena tu voz
        else:
            audio.reproducir("notificacion") # Pitido por defecto estilo radio

    def ocultar(self):
        self.activo = False

    def actualizar(self, dt):
        if self.activo and self.escritor:
            self.escritor.actualizar(dt)

    def dibujar(self, superficie):
        if not self.activo:
            return
        
        surf_fondo = pygame.Surface((self.rect_fondo.width, self.rect_fondo.height), pygame.SRCALPHA)
        surf_fondo.fill(self.color_fondo)
        superficie.blit(surf_fondo, (self.rect_fondo.x, self.rect_fondo.y))
        
        pygame.draw.line(superficie, self.color_nombre, (0, self.rect_fondo.y), (config.WIDTH, self.rect_fondo.y), 2)
        
        nombre_surf = self.fuente_nombre.render(self.nombre, True, self.color_nombre)
        superficie.blit(nombre_surf, (20, config.HEIGHT - 50))
        
        if self.escritor:
            self.escritor.dibujar(superficie)