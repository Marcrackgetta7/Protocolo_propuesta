# main.py
import pygame
import sys
import config
from core.state_machine import StateMachine
from states.auth import Auth 
from states.main_menu import MainMenu
from states.intro import Intro
from states.achievements import Achievements

from states.minigame import Minigame       
from states.xmas_minigame import XmasMinigame 
from states.xmas_maze import XmasMaze       
from states.xmas_delivery import XmasDelivery 
from states.xmas_boss import XmasBoss 

from states.maze import Maze 
from states.boss import Boss 
from states.gallery import Gallery 
from states.proposal import Proposal
from states.outro import Outro
from states.settings import Settings
from states.interlude import Interlude 
from states.credits import Credits     
from utils.scanlines import Scanlines
from utils import audio
from utils import save_manager 

def main():
    pygame.mixer.pre_init(44100, -16, 2, 128) 
    pygame.init()
    audio.inicializar()
    
    audio.cargar_sonido("tecla", "assets/audio/tecla.wav", volumen=0.2) 
    audio.cargar_sonido("anomalia", "assets/audio/anomalia.wav", volumen=0.6)
    audio.cargar_sonido("disparo_jugador", "assets/audio/disparos.wav", volumen=0.3)
    audio.cargar_sonido("disparo_boss", "assets/audio/disparos_boss.wav", volumen=0.4)
    audio.cargar_sonido("boss_area", "assets/audio/Boss_ataque_area.wav", volumen=0.5)
    audio.cargar_sonido("explosion", "assets/audio/explosion.wav", volumen=0.7)
    audio.cargar_sonido("glitch", "assets/audio/glitch.wav", volumen=0.8)
    audio.cargar_sonido("laser_final", "assets/audio/Laser_boss_final.wav", volumen=0.8)
    audio.cargar_sonido("laser_fase1", "assets/audio/Laser_fase1.wav", volumen=0.5)
    
    flags = pygame.SCALED | pygame.RESIZABLE
    pantalla = pygame.display.set_mode((config.WIDTH, config.HEIGHT), flags)
    pygame.display.set_caption("Protocolo: Brecha")
    reloj = pygame.time.Clock()
    filtro_crt = Scanlines()

    # --- DIÁLOGOS DE LAS CINEMÁTICAS ---
    textos_in_1 = ["¡Bienvenida a este Cuento de Navidad!", "Los regalos se han caído del trineo en pleno vuelo.", "¡Ayúdame a atraparlos antes de que se rompan!"]
    textos_out_1 = ["¡Uf! Salvamos los regalos a tiempo.", "Pero hemos aterrizado en medio de la nada...", "Debemos encontrar el camino en el Bosque Nevado."]

    textos_in_2 = ["El Bosque Nevado es tranquilo, pero confuso.", "Busca las 4 esferas doradas para activar el portal verde.", "Si te sientes perdida, yo te guiaré."]
    textos_out_2 = ["¡Encontraste la salida!", "El frío empieza a calar los huesos, pero la aldea está cerca.", "¡Vamos, los niños esperan!"]

    textos_in_3 = ["¡Llegamos a la aldea a tiempo!", "Acércate a las casas para dejar los regalos.", "¡Hazlo rápido, antes de que amanezca en 15 segundos!"]
    textos_out_3 = ["¡Trabajo perfecto, entregas completadas!", "Espera... ¿qué es ese ruido gigante?", "¡El suelo está temblando!"]

    textos_in_4 = ["¡Oh no! Has despertado al Muñeco Gruñón.", "Lánzale regalos con ESPACIO para calmar su furia.", "¡No dejes que el frío te congele!"]
    textos_out_4 = ["¡El Muñeco ha sido derrotado!", "Pero algo no está bien...", "La nieve... se está deshaciendo en código fuente...", "[ ALERTA: BRECHA DETECTADA ]"]

    textos_out_5 = ["> ANOMALÍA RECUPERADA...", "> El sistema central ha detectado nuestra presencia.", "> Nos han encerrado en el laberinto de cortafuegos."]

    textos_in_6 = ["> Nivel de seguridad máximo.", "> El laberinto está patrullado por Limpiadores.", "> Rompe los cortafuegos y encuentra la salida."]
    textos_out_6 = ["> CORTAFUEGOS DERRIBADOS.", "> Acceso al Núcleo principal concedido.", "> Prepárate... esto no será nada fácil."]

    textos_in_7 = ["> ADVERTENCIA: NÚCLEO INESTABLE.", "> Su escudo es impenetrable a largo plazo.", "> Mantente con vida y esquiva el barrido láser."]

    diccionario_estados = {
        "AUTH": Auth(),
        "MAIN_MENU": MainMenu(),
        "INTRO": Intro(), # Intro especial glitcheada de la fase 5
        "ACHIEVEMENTS": Achievements(),
        
        # FLUJOS CINEMÁTICOS
        "INTRO_1": Interlude(textos_in_1, "XMAS_MINIGAME"),
        "XMAS_MINIGAME": XmasMinigame(), 
        "OUTRO_1": Interlude(textos_out_1, "INTRO_2"),
        
        "INTRO_2": Interlude(textos_in_2, "XMAS_MAZE"),   
        "XMAS_MAZE": XmasMaze(), 
        "OUTRO_2": Interlude(textos_out_2, "INTRO_3"),
        
        "INTRO_3": Interlude(textos_in_3, "XMAS_DELIVERY"),   
        "XMAS_DELIVERY": XmasDelivery(), 
        "OUTRO_3": Interlude(textos_out_3, "INTRO_4"),
        
        "INTRO_4": Interlude(textos_in_4, "XMAS_BOSS"),   
        "XMAS_BOSS": XmasBoss(), 
        "OUTRO_4": Interlude(textos_out_4, "MAIN_MENU"),
        
        "MINIGAME": Minigame(), 
        "OUTRO_5": Interlude(textos_out_5, "INTRO_6"),
        
        "INTRO_6": Interlude(textos_in_6, "HACK_MAZE"),   
        "HACK_MAZE": Maze(), 
        "OUTRO_6": Interlude(textos_out_6, "INTRO_7"),
        
        "INTRO_7": Interlude(textos_in_7, "HACK_BOSS"),   
        "HACK_BOSS": Boss(),
        
        "SETTINGS": Settings(),
        "CREDITS": Credits(),     
        "GALLERY": Gallery(),                     
        "PROPOSAL": Proposal(),
        "OUTRO": Outro()
    }
    
    maquina = StateMachine(diccionario_estados, "AUTH")
    if getattr(maquina.state, "es_partida", False):
        maquina.mostrando_controles = True

    ejecutando = True
    while ejecutando:
        dt = reloj.tick(config.FPS) / 1000.0 
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: ejecutando = False
            maquina.manejar_eventos(evento)
        if maquina.state.quit: ejecutando = False

        estado_antes = maquina.state_name
        maquina.actualizar(dt)
        estado_despues = maquina.state_name
        
        if estado_antes != estado_despues:
            audio.detener_sonido("tecla")
            if estado_despues == "MAIN_MENU":
                audio.detener_musica() 

        maquina.dibujar(pantalla)
        filtro_crt.dibujar(pantalla)
        
        from utils.toast import ToastManager
        ToastManager.get().actualizar(dt)
        ToastManager.get().dibujar(pantalla)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()