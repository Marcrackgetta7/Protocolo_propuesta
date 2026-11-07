import math
import pygame
from utils.fonts import get_font
from states.base_state import BaseState
from utils.text_renderer import TypewriterText
from utils import audio
from utils import save_manager
from utils.vfx import GlowCache, GradientCache, ProceduralUI
import config


class Auth(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "MAIN_MENU"
        self.fuente_titulo = get_font(22, bold=True)
        self.fuente_input = get_font(24, bold=True)
        self.fuente_ui = get_font(14)

        self.preguntas = [
            "PREGUNTA 1/3:\n¿Con qué apodo me sueles llamar?",
            "PREGUNTA 2/3:\n¿Cómo se llama nuestra mascota?",
            "PREGUNTA 3/3:\n¿Cuáles profesores me sobreexplotan?"
        ]

        # Validación inteligente (ignora mayúsculas y espacios extra)
        self.respuestas = [
            lambda txt: "marce" in txt.lower(),
            lambda txt: "kazari" in txt.lower(),
            lambda txt: "joel" in txt.lower() and "roberto" in txt.lower()
        ]

        self.paso = 0
        self.input_text = ""
        self.mensaje_error = ""
        self.timer_error = 0.0

        self.escritor = None
        self.estado_fase = "ESCRIBIENDO"
        self.timer_exito = 0.0
        self.tiempo = 0.0

        self.bg_surf = GradientCache.get_vertical(
            config.WIDTH, config.HEIGHT, (6, 8, 16), (16, 6, 14), vignette=True
        )
        self.marco_terminal = pygame.Rect(20, 20, config.WIDTH - 40, config.HEIGHT - 40)
        self.caja_input = pygame.Rect(42, 248, config.WIDTH - 120, 48)

    def startup(self):
        # Si ya se autenticó antes, salta esta pantalla instantáneamente
        datos = save_manager.cargar()
        if datos.get("autenticado", False):
            self.done = True
            return

        self.paso = 0
        self.input_text = ""
        self.mostrar_pregunta()
        audio.reproducir_musica("assets/audio/Fase1_dark.ogg", volumen=0.3)

    def mostrar_pregunta(self):
        self.input_text = ""
        self.mensaje_error = ""
        self.estado_fase = "ESCRIBIENDO"
        texto = f"> PROTOCOLO DE SEGURIDAD ACTIVADO.\n> IDENTIDAD REQUERIDA PARA ACCEDER A LOS ARCHIVOS DE MARCELO.\n\n{self.preguntas[self.paso]}"
        self.escritor = TypewriterText(self.fuente_titulo, texto, (50, 70), speed=0.03, max_width=config.WIDTH - 100)

    def manejar_eventos(self, evento):
        if self.estado_fase == "ESPERANDO_INPUT":
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    # Verifica la respuesta
                    if self.respuestas[self.paso](self.input_text):
                        # Guardar respuesta
                        save_manager.guardar(answer_key=f"q{self.paso + 1}", answer_val=self.input_text)

                        self.paso += 1
                        audio.reproducir("tecla")
                        if self.paso >= len(self.preguntas):
                            self.estado_fase = "COMPLETADO"
                            save_manager.guardar(autenticado=True)
                            audio.detener_musica()
                            audio.reproducir("anomalia")
                        else:
                            self.mostrar_pregunta()
                    else:
                        self.mensaje_error = "ACCESO DENEGADO. RESPUESTA INCORRECTA."
                        self.timer_error = 2.0
                        self.input_text = ""
                        audio.reproducir("explosion")
                elif evento.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                    audio.reproducir("tecla", anti_spam_ms=50)
                else:
                    # Escribir letras (límite de 40 caracteres)
                    if len(self.input_text) < 40 and evento.unicode.isprintable():
                        self.input_text += evento.unicode
                        audio.reproducir("tecla", anti_spam_ms=50)

    def actualizar(self, dt):
        self.tiempo += dt
        if self.estado_fase == "ESCRIBIENDO":
            if self.escritor:
                self.escritor.actualizar(dt)
                if self.escritor.finished:
                    self.estado_fase = "ESPERANDO_INPUT"

        elif self.estado_fase == "ESPERANDO_INPUT":
            if self.timer_error > 0:
                self.timer_error -= dt

        elif self.estado_fase == "COMPLETADO":
            self.timer_exito += dt
            if self.timer_exito > 2.5:  # Espera 2.5 seg para que lea que pasó
                self.done = True

    def dibujar(self, superficie):
        superficie.blit(self.bg_surf, (0, 0))
        ProceduralUI.draw_panel(
            superficie, self.marco_terminal,
            bg_color=(12, 10, 18, 210),
            border_color=config.COLOR_ENERGY,
            cut=16,
            glow=False
        )

        # Indicadores de progreso de seguridad (3 nodos arriba a la derecha)
        for i in range(3):
            nx = config.WIDTH - 120 + i * 30
            ny = 48
            activo = i < self.paso or self.estado_fase == "COMPLETADO"
            col_nodo = (50, 255, 100) if activo else (config.COLOR_ENERGY if i == self.paso else (70, 70, 85))
            if activo or i == self.paso:
                GlowCache.blit(superficie, nx, ny, 14, col_nodo, intensity=0.5)
            pygame.draw.circle(superficie, col_nodo, (nx, ny), 6 if activo else 5, 0 if activo else 2)

        if self.estado_fase in ["ESCRIBIENDO", "ESPERANDO_INPUT"]:
            if self.escritor:
                self.escritor.dibujar(superficie)

        if self.estado_fase == "ESPERANDO_INPUT":
            ProceduralUI.draw_panel(
                superficie, self.caja_input,
                bg_color=(20, 14, 28, 225),
                border_color=config.COLOR_DANGER if self.timer_error > 0 else config.COLOR_ENERGY,
                cut=8,
                glow=True
            )
            cursor = "_" if math.sin(self.tiempo * 7.0) > 0 else ""
            txt_input = self.fuente_input.render(f"> {self.input_text}{cursor}", True, config.COLOR_ENERGY)
            superficie.blit(txt_input, (54, 258))

            inst = self.fuente_ui.render("[ ESCRIBE TU RESPUESTA Y PRESIONA ENTER ]", True, (150, 150, 165))
            superficie.blit(inst, (50, 312))

            if self.timer_error > 0:
                GlowCache.blit(superficie, 260, 362, 70, config.COLOR_DANGER, intensity=0.4)
                err = self.fuente_titulo.render(self.mensaje_error, True, config.COLOR_DANGER)
                superficie.blit(err, (50, 350))

        elif self.estado_fase == "COMPLETADO":
            GlowCache.blit(superficie, config.WIDTH // 2, config.HEIGHT // 2, 140, (50, 255, 100), intensity=0.45)
            txt = self.fuente_titulo.render("> IDENTIDAD CONFIRMADA. BIENVENIDA.", True, (50, 255, 50))
            superficie.blit(txt, txt.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2)))
