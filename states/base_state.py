import pygame

class BaseState:
    """Clase base de la que heredarán todas las fases del juego."""
    def __init__(self):
        self.done = False         # Cambia a True cuando la fase termina
        self.quit = False         # Cambia a True si el jugador cierra el juego
        self.next_state = None    # Nombre de la siguiente fase a cargar
        # Fuente tipo consola básica para empezar (la cambiaremos en la Fase 4)
        self.font = pygame.font.SysFont("consolas", 24) 

    def startup(self):
        """Se ejecuta al entrar a este estado."""
        pass

    def cleanup(self):
        """Se ejecuta justo antes de salir de este estado."""
        pass

    def manejar_eventos(self, evento):
        """Procesa los inputs del jugador (teclado, ratón)."""
        pass

    def actualizar(self, dt):
        """Lógica del juego (movimiento, temporizadores). dt = delta time."""
        pass

    def dibujar(self, superficie):
        """Renderiza los elementos en pantalla."""
        pass