import pygame
import config
from utils import audio

class TypewriterText:
    def __init__(self, font, text, pos, speed=0.04):
        self.font = font
        self.text = text
        self.pos = pos
        self.speed = speed
        self.current_text = ""
        self.index = 0
        self.timer = 0.0
        self.finished = False

    def actualizar(self, dt):
        if not self.finished:
            self.timer += dt
            if self.timer >= self.speed:
                self.timer = 0.0
                self.index += 1
                self.current_text = self.text[:self.index]
                
                if self.text[self.index - 1] != " " and self.text[self.index - 1] != "\n":
                    audio.reproducir("tecla", anti_spam_ms=40, parar_anterior=True)
                    
                if self.index >= len(self.text):
                    self.finished = True
                    audio.detener_sonido("tecla") 
                    
    def dibujar(self, superficie, alpha=255):
        lineas = self.current_text.split('\n')
        y_offset = self.pos[1]
        for linea in lineas:
            texto_surface = self.font.render(linea, True, config.COLOR_TEXT)
            if alpha < 255:
                texto_surface.set_alpha(alpha) # Vuelve el texto transparente
            superficie.blit(texto_surface, (self.pos[0], y_offset))
            y_offset += 30