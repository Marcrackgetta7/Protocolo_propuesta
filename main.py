# main.py
import pygame
import sys
import config
from core.state_machine import StateMachine
from states.main_menu import MainMenu
from states.intro import Intro
from states.minigame import Minigame
from states.maze import Maze 
from states.boss import Boss 
from states.gallery import Gallery # <--- Importamos la nueva Galería Secreta
from states.proposal import Proposal
from states.outro import Outro
from states.interlude import Interlude 
from states.credits import Credits     
from utils.scanlines import Scanlines
from utils import audio
from utils import save_manager 

def main():
    pygame.mixer.pre_init(44100, -16, 2, 128) 
    pygame.init()
    audio.inicializar()
    
    # --- EFECTOS DE SONIDO ---
    audio.cargar_sonido("tecla", "assets/audio/tecla.wav", volumen=0.2) 
    audio.cargar_sonido("anomalia", "assets/audio/anomalia.wav", volumen=0.6)
    audio.cargar_sonido("disparo_jugador", "assets/audio/disparos.wav", volumen=0.3)
    audio.cargar_sonido("disparo_boss", "assets/audio/disparos_boss.wav", volumen=0.4)
    audio.cargar_sonido("boss_area", "assets/audio/Boss_ataque_area.wav", volumen=0.5)
    audio.cargar_sonido("explosion", "assets/audio/explosion.wav", volumen=0.7)
    audio.cargar_sonido("glitch", "assets/audio/glitch.wav", volumen=0.8)
    audio.cargar_sonido("laser_final", "assets/audio/Laser_boss_final.wav", volumen=0.8)
    audio.cargar_sonido("laser_fase1", "assets/audio/Laser_fase1.wav", volumen=0.5)
    
    # --- VOCES IA ---
    audio.cargar_sonido("v_f1_in", "assets/audio/v_f1_in.wav", volumen=1.0)
    audio.cargar_sonido("v_f1_mid", "assets/audio/v_f1_mid.wav", volumen=1.0)
    audio.cargar_sonido("v_f1_fin", "assets/audio/v_f1_fin.wav", volumen=1.0)
    audio.cargar_sonido("v_f2_in", "assets/audio/v_f2_in.wav", volumen=1.0)
    audio.cargar_sonido("v_f2_hack", "assets/audio/v_f2_hack.wav", volumen=1.0)
    audio.cargar_sonido("v_f2_roto", "assets/audio/v_f2_roto.wav", volumen=1.0)
    audio.cargar_sonido("v_f2_dead", "assets/audio/v_f2_dead.wav", volumen=1.0)
    audio.cargar_sonido("v_f3_in", "assets/audio/v_f3_in.wav", volumen=1.0)
    audio.cargar_sonido("v_f3_esc", "assets/audio/v_f3_esc.wav", volumen=1.0)
    audio.cargar_sonido("v_f3_win", "assets/audio/v_f3_win.wav", volumen=1.0)
    audio.cargar_sonido("v_f3_alert", "assets/audio/v_f3_alert.wav", volumen=1.0)
    audio.cargar_sonido("v_f3_crit", "assets/audio/v_f3_crit.wav", volumen=1.0)
    audio.cargar_sonido("v_f3_sac1", "assets/audio/v_f3_sac1.wav", volumen=1.0)
    audio.cargar_sonido("v_f3_sac2", "assets/audio/v_f3_sac2.wav", volumen=1.0)
    
    flags = pygame.SCALED | pygame.RESIZABLE
    pantalla = pygame.display.set_mode((config.WIDTH, config.HEIGHT), flags)
    pygame.display.set_caption("Protocolo: Brecha")
    reloj = pygame.time.Clock()
    filtro_crt = Scanlines()

    textos_inter_1 = [
        "> ANOMALÍA 01 RECUPERADA...",
        "> El sistema intenta aislar los recuerdos de nuestra amistad.",
        "> Te he abierto una puerta trasera. Entra al laberinto oscuro y busca la salida."
    ]
    textos_inter_2 = [
        "> CORTAFUEGOS BURLADOS.",
        "> Advertencia: Niveles críticos de cafeína detectados en el sistema.",
        "> Alerta de intrusión: Entidad 'enano' detectada en el sector 4.",
        "> El núcleo nos ha descubierto... ¡Prepárate para luchar!"
    ]

    estado_minigame = Minigame()
    estado_minigame.next_state = "MAIN_MENU" 
    estado_maze = Maze()
    estado_maze.next_state = "MAIN_MENU" 
    estado_boss = Boss()
    estado_boss.next_state = "CREDITS" 
    estado_outro = Outro()
    estado_outro.next_state = "MAIN_MENU" 

    diccionario_estados = {
        "MAIN_MENU": MainMenu(),
        "INTRO": Intro(),
        "MINIGAME": estado_minigame, 
        "INTER_1": Interlude(textos_inter_1, "MAZE"),   
        "MAZE": estado_maze, 
        "INTER_2": Interlude(textos_inter_2, "BOSS"),   
        "BOSS": estado_boss, 
        "CREDITS": Credits(),     
        "GALLERY": Gallery(), # <--- Integramos el nivel secreto                      
        "PROPOSAL": Proposal(),
        "OUTRO": estado_outro
    }
    
    maquina = StateMachine(diccionario_estados, "MAIN_MENU")

    ejecutando = True
    while ejecutando:
        dt = reloj.tick(config.FPS) / 1000.0 

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            maquina.manejar_eventos(evento)

        if maquina.state.quit:
            ejecutando = False

        estado_antes = maquina.state_name
        maquina.actualizar(dt)
        estado_despues = maquina.state_name
        
        # INTERRUPTOR GENERAL: Si cambiamos de pantalla, MATAMOS el sonido de tecleo
        if estado_antes != estado_despues:
            audio.detener_sonido("tecla")
            
            if estado_despues == "MAIN_MENU":
                if estado_antes == "MINIGAME": save_manager.guardar(2) 
                elif estado_antes == "MAZE": save_manager.guardar(3) 
                elif estado_antes == "CREDITS": save_manager.guardar(4) 
                elif estado_antes == "OUTRO": save_manager.guardar(5) 

        maquina.dibujar(pantalla)
        filtro_crt.dibujar(pantalla)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()