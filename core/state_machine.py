from utils.pause_menu import PauseMenu
import pygame

class StateMachine:
    """Gestor que controla qué fase del juego está activa."""
    def __init__(self, states_dict, start_state):
        self.states = states_dict                 # Diccionario con las fases instanciadas
        self.state_name = start_state             # Nombre de la fase inicial
        self.state = self.states[self.state_name] # Objeto de la fase actual
        self.pausado = False
        self.pause_menu = PauseMenu(self)
        self.state.startup()                      # Arrancar la primera fase

    def cambiar_estado(self):
        """Revisa si la fase actual terminó y pasa a la siguiente."""
        if self.state.done:
            next_name = self.state.next_state
            if next_name not in self.states:
                print(f"Error: Estado '{next_name}' no existe en el diccionario de estados.")
                self.state.done = False
                return
            self.state.cleanup()
            self.state_name = next_name
            self.state.done = False
            self.state = self.states[self.state_name]
            self.pausado = False
            self.state.startup()

    def manejar_eventos(self, evento):
        if self.pausado:
            self.pause_menu.manejar_eventos(evento)
            return
            
        es_partida = getattr(self.state, "es_partida", False)
        if es_partida and evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self.pausado = True
            return

        self.state.manejar_eventos(evento)

    def actualizar(self, dt):
        self.cambiar_estado()
        if self.pausado:
            self.pause_menu.actualizar(dt)
            return
        self.state.actualizar(dt)

    def dibujar(self, superficie):
        self.state.dibujar(superficie)
        if self.pausado:
            self.pause_menu.dibujar(superficie)