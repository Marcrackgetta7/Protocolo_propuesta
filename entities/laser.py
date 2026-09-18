import pygame
import config

class Laser:
    def __init__(self, es_horizontal, pos):
        self.es_horizontal = es_horizontal
        self.pos = pos
        self.timer = 0.0
        # ¡MÁS RÁPIDO! Exige mejores reflejos (antes era 1.0)
        self.tiempo_aviso = 0.6  
        self.tiempo_activo = 0.3
        self.terminado = False
        self.estado = "AVISO"
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.grosor = 30

    def actualizar(self, dt):
        self.timer += dt
        if self.estado == "AVISO":
            if self.timer >= self.tiempo_aviso:
                self.estado = "ACTIVO"
                self.timer = 0.0
        elif self.estado == "ACTIVO":
            if self.timer >= self.tiempo_activo:
                self.terminado = True

    def dibujar(self, superficie):
        if self.es_horizontal:
            self.rect = pygame.Rect(0, self.pos - self.grosor//2, config.WIDTH, self.grosor)
        else:
            self.rect = pygame.Rect(self.pos - self.grosor//2, 0, self.grosor, config.HEIGHT)

        if self.estado == "AVISO":
            # ¡ALTA VISIBILIDAD! Un gris muy claro que contrasta perfecto con el fondo
            pygame.draw.rect(superficie, (200, 200, 200), self.rect, 2)
        elif self.estado == "ACTIVO":
            pygame.draw.rect(superficie, config.COLOR_DANGER, self.rect)