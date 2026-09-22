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
        
        # Fade Transitions
        self.haciendo_fade_out = False
        self.haciendo_fade_in = False
        self.alpha_fade = 0.0
        self.fade_velocidad = 500.0
        self.estado_siguiente_nombre = ""

    def cambiar_estado(self):
        """Revisa si la fase actual terminó y comienza el fade de transición."""
        if self.state.done and not self.haciendo_fade_out and not self.haciendo_fade_in:
            self.estado_siguiente_nombre = self.state.next_state
            if self.estado_siguiente_nombre not in self.states:
                print(f"Error: Estado '{self.estado_siguiente_nombre}' no existe en el diccionario de estados.")
                self.state.done = False
                return
            
            # Guardar el tiempo invertido en la fase si era partida
            if getattr(self.state, "es_partida", False) and hasattr(self.state, "time_active"):
                import utils.save_manager as sm
                sm.guardar(phase_name=self.state_name, phase_time_add=self.state.time_active, total_time_add=self.state.time_active)
                self.state.time_active = 0.0 # reset for future retries
            
            self.haciendo_fade_out = True
            self.alpha_fade = 0.0
            self.state.done = False # Evita múltiples activaciones

    def manejar_eventos(self, evento):
        if getattr(self, "mostrando_controles", False):
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
                self.mostrando_controles = False
            return
            
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
        
        # Progreso del fade out
        if self.haciendo_fade_out:
            self.alpha_fade += self.fade_velocidad * dt
            if self.alpha_fade >= 255.0:
                self.alpha_fade = 255.0
                self.haciendo_fade_out = False
                # Cambio real de estado
                self.state.cleanup()
                self.state_name = self.estado_siguiente_nombre
                self.state = self.states[self.state_name]
                self.pausado = False
                self.state.startup()
                self.haciendo_fade_in = True
        
        # Progreso del fade in
        elif self.haciendo_fade_in:
            self.alpha_fade -= self.fade_velocidad * dt
            if self.alpha_fade <= 0.0:
                self.alpha_fade = 0.0
                self.haciendo_fade_in = False
                if getattr(self.state, "es_partida", False):
                    self.mostrando_controles = True

        if self.pausado:
            self.pause_menu.actualizar(dt)
            return
            
        if getattr(self, "mostrando_controles", False):
            return # Detener la lógica de la partida mientras se muestran los controles
            
        # Solo actualizamos el estado si no estamos en pleno fade out oscuro
        if not (self.haciendo_fade_out and self.alpha_fade > 200):
            self.state.actualizar(dt)
            
            # Control de tiempo por fase
            if getattr(self.state, "es_partida", False) and not self.pausado and not getattr(self, "mostrando_controles", False):
                if not hasattr(self.state, "time_active"):
                    self.state.time_active = 0.0
                self.state.time_active += dt

    def dibujar(self, superficie):
        self.state.dibujar(superficie)
        if self.pausado:
            self.pause_menu.dibujar(superficie)
            
        if getattr(self, "mostrando_controles", False):
            import config
            overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            superficie.blit(overlay, (0, 0))
            
            fuente_tit = pygame.font.SysFont("consolas", 36, bold=True)
            fuente_txt = pygame.font.SysFont("consolas", 24)
            
            tit = fuente_tit.render("CONTROLES DE LA FASE", True, config.COLOR_ENERGY)
            superficie.blit(tit, tit.get_rect(center=(config.WIDTH//2, 150)))
            
            controles = getattr(self.state, "textos_controles", [
                "Movimiento: Teclas W,A,S,D o Flechas",
                "Acción Principal: Barra ESPACIADORA",
                "Pausa del Sistema: Tecla ESCAPE"
            ])
            
            for i, texto in enumerate(controles):
                linea = fuente_txt.render(texto, True, (255, 255, 255))
                superficie.blit(linea, linea.get_rect(center=(config.WIDTH//2, 230 + i * 40)))
                
            txt_cont = fuente_txt.render("Presiona [ESPACIO] para iniciar", True, (150, 200, 255))
            # Efecto parpadeo
            if pygame.time.get_ticks() % 1000 < 500:
                superficie.blit(txt_cont, txt_cont.get_rect(center=(config.WIDTH//2, config.HEIGHT - 100)))

        if self.haciendo_fade_out or self.haciendo_fade_in:
            overlay = pygame.Surface(superficie.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, int(max(0, min(255, self.alpha_fade)))))
            superficie.blit(overlay, (0, 0))