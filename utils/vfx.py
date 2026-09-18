import random

class ScreenShake:
    """Clase para manejar el efecto de temblor de cámara."""
    def __init__(self):
        self.intensidad = 0
        self.duracion = 0.0

    def iniciar(self, intensidad, duracion):
        self.intensidad = intensidad
        self.duracion = duracion

    def actualizar(self, dt):
        if self.duracion > 0:
            self.duracion -= dt
        else:
            self.intensidad = 0
            self.duracion = 0.0

    def obtener_offset(self):
        # Genera coordenadas aleatorias basadas en la intensidad
        if self.intensidad > 0:
            ox = random.randint(-self.intensidad, self.intensidad)
            oy = random.randint(-self.intensidad, self.intensidad)
            return ox, oy
        return 0, 0