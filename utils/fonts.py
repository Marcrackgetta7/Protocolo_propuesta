import pygame
import os

_cache = {}

def get_font(size, bold=False, italic=False):
    key = (size, bold, italic)
    if key not in _cache:
        # Usamos la fuente TTF empaquetada para asegurar compatibilidad en WebAssembly
        ruta = os.path.join("assets", "fonts", "JetBrainsMono.ttf")
        try:
            fuente = pygame.font.Font(ruta, size)
            if bold:
                fuente.set_bold(True)
            if italic:
                fuente.set_italic(True)
            _cache[key] = fuente
        except Exception as e:
            print(f"Error cargando fuente {ruta}: {e}. Usando fallback.")
            _cache[key] = pygame.font.SysFont("consolas", size, bold, italic)
    
    return _cache[key]
