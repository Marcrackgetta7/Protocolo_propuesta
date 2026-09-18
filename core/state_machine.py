class StateMachine:
    """Gestor que controla qué fase del juego está activa."""
    def __init__(self, states_dict, start_state):
        self.states = states_dict                 # Diccionario con las fases instanciadas
        self.state_name = start_state             # Nombre de la fase inicial
        self.state = self.states[self.state_name] # Objeto de la fase actual
        self.state.startup()                      # Arrancar la primera fase

    def cambiar_estado(self):
        """Revisa si la fase actual terminó y pasa a la siguiente."""
        if self.state.done:
            self.state.cleanup()
            self.state_name = self.state.next_state
            self.state.done = False
            self.state = self.states[self.state_name]
            self.state.startup()

    def manejar_eventos(self, evento):
        self.state.manejar_eventos(evento)

    def actualizar(self, dt):
        self.cambiar_estado()
        self.state.actualizar(dt)

    def dibujar(self, superficie):
        self.state.dibujar(superficie)