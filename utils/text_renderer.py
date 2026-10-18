import pygame
import config
from utils import audio

def wrap_text(font, text, max_width):
    if not max_width:
        return text
    paragraphs = text.split('\n')
    wrapped_paragraphs = []
    for p in paragraphs:
        if not p:
            wrapped_paragraphs.append("")
            continue
        words = p.split(' ')
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    wrapped_paragraphs.append(' '.join(current_line))
                    current_line = [word]
                else:
                    wrapped_paragraphs.append(word)
                    current_line = []
        if current_line:
            wrapped_paragraphs.append(' '.join(current_line))
    return '\n'.join(wrapped_paragraphs)

class TypewriterText:
    def __init__(self, font, text, pos, speed=0.04, max_width=None):
        self.font = font
        self.pos = pos
        self.speed = speed
        if max_width is None and config.WIDTH:
            max_width = max(200, config.WIDTH - pos[0] - 25)
        self.max_width = max_width
        self.text = wrap_text(font, text, max_width)
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
        line_height = max(24, self.font.get_linesize() + 2)
        for linea in lineas:
            if linea:
                texto_surface = self.font.render(linea, True, config.COLOR_TEXT)
                if alpha < 255:
                    texto_surface.set_alpha(alpha) # Vuelve el texto transparente
                superficie.blit(texto_surface, (self.pos[0], y_offset))
            y_offset += line_height