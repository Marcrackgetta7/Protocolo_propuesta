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
from states.stats import Stats
from states.interlude import Interlude 
from states.credits import Credits     
from utils.scanlines import Scanlines
from utils import audio
from utils import save_manager 

import asyncio

async def main():
    pygame.mixer.pre_init(44100, -16, 2, 4096) 
    pygame.init()
    pantalla = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.display.set_caption("Protocolo: Brecha")

    if sys.platform == "emscripten":
        import platform
        try:
            platform.window.canvas.width = config.WIDTH
            platform.window.canvas.height = config.HEIGHT
            platform.window.config.fb_width = str(config.WIDTH)
            platform.window.config.fb_height = str(config.HEIGHT)
            platform.window.config.fb_ar = config.WIDTH / config.HEIGHT
            platform.window.config.gui_divider = 1
            platform.window.window_resize()
        except Exception:
            pass

    audio.inicializar()
    
    audio.cargar_sonido("tecla", "assets/audio/tecla.ogg", volumen=0.2) 
    audio.cargar_sonido("anomalia", "assets/audio/anomalia.ogg", volumen=0.6)
    audio.cargar_sonido("disparo_jugador", "assets/audio/disparos.ogg", volumen=0.3)
    audio.cargar_sonido("disparo_boss", "assets/audio/disparos_boss.ogg", volumen=0.4)
    audio.cargar_sonido("boss_area", "assets/audio/Boss_ataque_area.ogg", volumen=0.5)
    audio.cargar_sonido("explosion", "assets/audio/explosion.ogg", volumen=0.7)
    audio.cargar_sonido("glitch", "assets/audio/glitch.ogg", volumen=0.8)
    audio.cargar_sonido("laser_final", "assets/audio/Laser_boss_final.ogg", volumen=0.8)
    audio.cargar_sonido("laser_fase1", "assets/audio/Laser_fase1.ogg", volumen=0.5)
    
    reloj = pygame.time.Clock()
    filtro_crt = Scanlines()

    # --- DIALOGOS DE LAS CINEMATICAS ---
    textos_in_1 = [
        "¡Bienvenida a este Cuento de Navidad!", 
        "Una sacudida en el cielo hizo que los regalos cayeran del trineo.", 
        "¡Ayúdame a atraparlos todos antes de que se rompan contra el suelo!"
    ]
    textos_out_1 = [
        "¡Uf! Salvamos hasta el último regalo justo a tiempo.", 
        "Pero el aterrizaje forzoso nos dejó en medio de la nada...", 
        "Debemos cruzar el Bosque Nevado para retomar el rumbo."
    ]

    textos_in_2 = [
        "El Bosque Nevado parece tranquilo, pero sus caminos engañan.", 
        "Busca las 4 esferas doradas para activar el portal verde.", 
        "No te preocupes si te sientes perdida, yo te guiaré desde aquí."
    ]
    textos_out_2 = [
        "¡Lograste activar el portal! Sabía que encontrarías la salida.", 
        "Qué raro... el cielo acaba de parpadear como una pantalla rota.", 
        "No importa, la aldea está frente a nosotros. ¡Vamos, los niños esperan!"
    ]

    textos_in_3 = [
        "¡Llegamos a la aldea! Pero el reloj avanza demasiado rápido.", 
        "Acércate a las casas para dejar los regalos que recuperamos.", 
        "¡Hazlo rápido, tienes 25 segundos antes de que amanezca!"
    ]
    textos_out_3 = [
        "¡Trabajo perfecto, todas las entregas están completas!", 
        "Espera... la música se detuvo de golpe. ¿Escuchas esa estática?", 
        "¡El suelo está temblando, algo está corrompiendo este mundo!"
    ]

    textos_in_4 = [
        "¡Cuidado! Una anomalía infectó al Muñeco de Nieve y lo volvió loco.", 
        "¡Lánzale regalos con ESPACIO para purificarlo y calmar su furia!", 
        "¡No te quedes quieta o su tormenta te congelará!"
    ]
    textos_out_4 = [
        "¡El Muñeco cayó! Pero el fallo ya se expandió demasiado...", 
        "Mira a tu alrededor: la nieve se está deshaciendo en código fuente...", 
        "[ ERROR CRÍTICO: CUENTO CORROMPIDO // BRECHA DETECTADA ]"
    ]

    textos_out_5 = [
        "> ANOMALÍA SUPERADA... Lograste escapar de esa trampa.", 
        "> El Glitch tomó el control del Sistema Central y quiere borrarnos.", 
        "> Nos acaba de encerrar en su laberinto de cortafuegos. ¡No te rindas!"
    ]

    textos_in_6 = [
        "> Nivel de corrupción: MÁXIMO. El sistema liberó a los Limpiadores.", 
        "> Son programas hostiles diseñados para eliminar todo a su paso.", 
        "> Rompe los cortafuegos del laberinto y abre una brecha hacia la salida."
    ]
    textos_out_6 = [
        "> ¡CORTAFUEGOS DERRIBADOS! Ni siquiera el código roto puede detenerte.", 
        "> Tenemos acceso directo al origen del fallo: el Núcleo Principal.", 
        "> Prepárate... si sobrevivimos a esto, recuperaremos el control."
    ]

    textos_in_7 = [
        "> ADVERTENCIA: EL NÚCLEO ESTÁ TOTALMENTE CORROMPIDO E INESTABLE.", 
        "> Su escudo de sobrecarga es impenetrable por ahora; no podrás dañarlo.", 
        "> ¡Mantente con vida y esquiva el barrido láser hasta que se agote!"
    ]
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
        "OUTRO_4": Interlude(textos_out_4, "INTRO"),
        
        "MINIGAME": Minigame(), 
        "OUTRO_5": Interlude(textos_out_5, "INTRO_6"),
        
        "INTRO_6": Interlude(textos_in_6, "HACK_MAZE"),   
        "HACK_MAZE": Maze(), 
        "OUTRO_6": Interlude(textos_out_6, "INTRO_7"),
        
        "INTRO_7": Interlude(textos_in_7, "HACK_BOSS"),   
        "HACK_BOSS": Boss(),
        
        "SETTINGS": Settings(),
        "STATS": Stats(),
        "CREDITS": Credits(),     
        "GALLERY": Gallery(),                     
        "PROPOSAL": Proposal(),
        "OUTRO": Outro()
    }
    
    maquina = StateMachine(diccionario_estados, "AUTH")
    if getattr(maquina.state, "es_partida", False):
        maquina.mostrando_controles = True

    if sys.platform == "emscripten":
        import platform
        try:
            platform.window.window_resize()
        except Exception:
            pass

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
        await asyncio.sleep(0) # Obligatorio para WebAssembly/Pygbag

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
