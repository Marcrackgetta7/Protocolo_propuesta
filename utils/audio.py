import pygame
import os

_sonidos = {}
_ultimo_play = {}

def inicializar():
    if not pygame.mixer.get_init():
        pygame.mixer.init()
        # Subimos de 8 a 32 canales para que ningún audio importante se corte
        pygame.mixer.set_num_channels(32) 

def cargar_sonido(nombre, ruta, volumen=0.5):
    if os.path.exists(ruta):
        sonido = pygame.mixer.Sound(ruta)
        sonido.set_volume(volumen)
        _sonidos[nombre] = sonido
    else:
        _sonidos[nombre] = None 
        print(f"Advertencia: No se encontró el audio '{nombre}' en {ruta}")

def reproducir(nombre, anti_spam_ms=0, parar_anterior=False):
    if nombre in _sonidos and _sonidos[nombre]:
        ahora = pygame.time.get_ticks()
        
        if anti_spam_ms > 0:
            if nombre in _ultimo_play and ahora - _ultimo_play[nombre] < anti_spam_ms:
                return
        
        # ¡LA MAGIA! Si el audio es largo, lo corta abruptamente antes de volver a sonarlo
        if parar_anterior:
            _sonidos[nombre].stop()
            
        _ultimo_play[nombre] = ahora
        _sonidos[nombre].play()

def detener_sonido(nombre):
    """Fuerza a un sonido específico a callarse inmediatamente."""
    if nombre in _sonidos and _sonidos[nombre]:
        _sonidos[nombre].stop()

def reproducir_musica(ruta, volumen=0.4, loop=-1):
    if os.path.exists(ruta):
        pygame.mixer.music.load(ruta)
        pygame.mixer.music.set_volume(volumen)
        pygame.mixer.music.play(loop)
    else:
        print(f"Advertencia: No se encontró la música de fondo en {ruta}")

def detener_musica():
    if pygame.mixer.get_init():
        pygame.mixer.music.fadeout(1000)