import pygame
import random
import math
import config

class UIButton:
    def __init__(self, x, y, ancho, alto, texto, evasivo=False):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.evasivo = evasivo
        self.fuente = pygame.font.SysFont("consolas", 24)
        self.color_normal = (40, 40, 40)
        self.color_hover = config.COLOR_ENERGY # Se ilumina en rosa al pasar el ratón
        self.intentos_evasion = 0
        self.visible = True

    def actualizar(self, pos_raton):
        if not self.visible:
            return

        # Lógica de evasión (IA de proximidad mediante distancia euclidiana)
        if self.evasivo:
            centro_x = self.rect.x + self.rect.width / 2
            centro_y = self.rect.y + self.rect.height / 2
            distancia = math.hypot(pos_raton[0] - centro_x, pos_raton[1] - centro_y)

            # Si el ratón se acerca a menos de 100 píxeles...
            if distancia < 100:
                self.intentos_evasion += 1
                
                # A los 5 intentos, el botón desaparece según el GDD
                if self.intentos_evasion > 5:
                    self.visible = False 
                else:
                    if self.intentos_evasion == 3:
                        self.texto = "¿Segura?"
                    elif self.intentos_evasion == 4:
                        self.texto = "Casi..."
                        
                    # Teletransportar a una posición aleatoria dentro de la pantalla
                    self.rect.x = random.randint(50, config.WIDTH - self.rect.width - 50)
                    self.rect.y = random.randint(50, config.HEIGHT - self.rect.height - 50)

    def dibujar(self, superficie, pos_raton):
        if not self.visible:
            return
        
        color_actual = self.color_hover if self.rect.collidepoint(pos_raton) else self.color_normal
        pygame.draw.rect(superficie, color_actual, self.rect)
        pygame.draw.rect(superficie, config.COLOR_TEXT, self.rect, 2) # Borde blanco tiza

        texto_surf = self.fuente.render(self.texto, True, config.COLOR_TEXT)
        texto_rect = texto_surf.get_rect(center=self.rect.center)
        superficie.blit(texto_surf, texto_rect)
        
    def clic(self, pos_raton, clic_izq):
        if self.visible and clic_izq and self.rect.collidepoint(pos_raton):
            return True
        return False