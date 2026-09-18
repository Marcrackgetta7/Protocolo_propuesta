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
                    # Al poner parar_anterior=True, si tu archivo es muy largo, solo sonará una fracción 
                    audio.reproducir("tecla", anti_spam_ms=40, parar_anterior=True)
                    
                if self.index >= len(self.text):
                    self.finished = True
                    # Cuando la frase termina, callamos el sonido a la fuerza
                    audio.detener_sonido("tecla") 
                    
    def dibujar(self, superficie):
        lineas = self.current_text.split('\n')
        y_offset = self.pos[1]
        for linea in lineas:
            texto_surface = self.font.render(linea, True, config.COLOR_TEXT)
            superficie.blit(texto_surface, (self.pos[0], y_offset))
            y_offset += 30