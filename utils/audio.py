import pygame
import os

_sonidos = {}
_ultimo_play = {}
_volumen_original = {}

_mult_sfx = 1.0
_mult_musica = 1.0
_musica_actual = None
_musica_vol_original = 0.4

def inicializar():
    if not pygame.mixer.get_init():
        pygame.mixer.init()
        pygame.mixer.set_num_channels(32)
        
    from utils import save_manager
    conf = save_manager.cargar().get("config", {"musica": 1.0, "sfx": 1.0})
    actualizar_volumenes(conf["musica"], conf["sfx"])

def actualizar_volumenes(musica, sfx):
    global _mult_musica, _mult_sfx, _musica_vol_original
    _mult_musica = musica
    _mult_sfx = sfx
    
    # Actualizar sonidos
    for nombre, sonido in _sonidos.items():
        if sonido:
            sonido.set_volume(_volumen_original.get(nombre, 0.5) * _mult_sfx)
            
    # Actualizar música en reproducción
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.set_volume(_musica_vol_original * _mult_musica)

def cargar_sonido(nombre, ruta, volumen=0.5):
    if os.path.exists(ruta):
        sonido = pygame.mixer.Sound(ruta)
        _volumen_original[nombre] = volumen
        sonido.set_volume(volumen * _mult_sfx)
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
        
        if parar_anterior:
            _sonidos[nombre].stop()
            
        _ultimo_play[nombre] = ahora
        _sonidos[nombre].play()

def detener_sonido(nombre):
    if nombre in _sonidos and _sonidos[nombre]:
        _sonidos[nombre].stop()

def reproducir_musica(ruta, volumen=0.4, loop=-1):
    global _musica_actual, _musica_vol_original
    if os.path.exists(ruta):
        _musica_actual = ruta
        _musica_vol_original = volumen
        pygame.mixer.music.load(ruta)
        pygame.mixer.music.set_volume(volumen * _mult_musica)
        pygame.mixer.music.play(loop)
    else:
        print(f"Advertencia: No se encontró la música de fondo en {ruta}")

def detener_musica():
    if pygame.mixer.get_init():
        pygame.mixer.music.fadeout(1000)