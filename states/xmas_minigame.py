import pygame
import random
from states.base_state import BaseState
from utils.companion import CompanionUI
from utils import audio
from utils import save_manager
import config

class Regalo:
    def __init__(self, velocidad, jx):
        self.rect = pygame.Rect(random.randint(50, config.WIDTH - 50), -30, 30, 30)
        # Hacemos que un porcentaje de los regalos apunten hacia el jugador para que sea más difícil
        if random.random() < 0.3:
            self.rect.x = jx
        self.y = -30.0
        self.vy = velocidad

    def actualizar(self, dt):
        self.y += self.vy * dt
        self.rect.y = int(self.y)

    def dibujar(self, sup):
        pygame.draw.rect(sup, (220, 20, 20), self.rect)
        pygame.draw.rect(sup, (20, 220, 20), (self.rect.x + 10, self.rect.y, 10, 30))
        pygame.draw.rect(sup, (20, 220, 20), (self.rect.x, self.rect.y + 10, 30, 10))

class XmasMinigame(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "MAIN_MENU" # Cancela la cinemática si abortas
        self.compañero = CompanionUI()
        self.jugador_rect = pygame.Rect(config.WIDTH//2 - 40, config.HEIGHT - 60, 80, 20)
        self.regalos = []
        self.score = 0
        self.regalos_perdidos = 0
        self.timer_spawn = 0.0
        self.ganado = False
        self.timer_victoria = 0.0
        self.es_partida = True
        self.fuente_ui = pygame.font.SysFont("consolas", 24, bold=True)

    def startup(self):
        self.score, self.regalos_perdidos = 0, 0
        self.regalos, self.ganado, self.timer_victoria = [], False, 0.0
        self.logros_obtenidos = save_manager.cargar().get("secretos", [])
        self.jugador_rect.x = config.WIDTH//2 - 40
        self.compañero.mostrar_mensaje("¡Feliz Navidad! Atrapa 10 regalos. ¡Si se caen, pierdes puntos!")
        audio.reproducir_musica("assets/audio/fase1_nav.ogg", volumen=0.4)

    def manejar_eventos(self, evento):
        pass

    def actualizar(self, dt):
        self.compañero.actualizar(dt)
        
        if self.ganado:
            self.timer_victoria += dt
            if self.timer_victoria > 1.5:
                save_manager.guardar(fase=2)
                self.done = True
            return

        teclas = pygame.key.get_pressed()
        # Balance: Canasta un 40% más rápida para que se sienta ágil
        vel = 550 * dt 
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]: self.jugador_rect.x -= vel
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: self.jugador_rect.x += vel
        if self.jugador_rect.left < 0: self.jugador_rect.left = 0
        if self.jugador_rect.right > config.WIDTH: self.jugador_rect.right = config.WIDTH

        intervalo = max(0.4, 1.2 - (self.score * 0.08))
        self.timer_spawn += dt
        if self.timer_spawn > intervalo:
            # Le enviamos la posición del jugador al regalo para que sepa dónde aparecer
            self.regalos.append(Regalo(150 + (self.score * 15), self.jugador_rect.centerx))
            self.timer_spawn = 0.0

        for r in self.regalos[:]:
            r.actualizar(dt)
            if r.rect.colliderect(self.jugador_rect):
                self.score += 1
                audio.reproducir("anomalia")
                self.regalos.remove(r)
                
                if self.score >= 10:
                    self.ganado = True
                    # Balance: Te permitimos que se te caiga 1 por accidente
                    if self.regalos_perdidos <= 1 and "L1" not in self.logros_obtenidos:
                        save_manager.guardar(secreto="L1")
                        self.compañero.mostrar_mensaje("¡LOGRO DESBLOQUEADO: Manos Ágiles!")
                        audio.reproducir("tecla")
                    else:
                        self.compañero.mostrar_mensaje("¡Nivel Completado! Avanzando...")
                        
            elif r.y > config.HEIGHT:
                self.regalos.remove(r)
                self.regalos_perdidos += 1
                if self.score > 0:
                    self.score -= 1
                    audio.reproducir("explosion")
                    self.compañero.mostrar_mensaje("¡Oh no! Se rompió un regalo. Perdiste 1 punto.")

    def dibujar(self, superficie):
        superficie.fill((20, 40, 60)) 
        tiempo = pygame.time.get_ticks() * 0.05
        for i in range(50):
            pygame.draw.circle(superficie, (255, 255, 255), ((i * 37) % config.WIDTH, (i * 53 + int(tiempo)) % config.HEIGHT), 2)
        
        for r in self.regalos: r.dibujar(superficie)
        pygame.draw.rect(superficie, (150, 100, 50), self.jugador_rect) 
        
        txt = self.fuente_ui.render(f"Regalos: {self.score}/10", True, (255, 255, 255))
        superficie.blit(txt, (20, 20))
        self.compañero.dibujar(superficie, self.jugador_rect.y)