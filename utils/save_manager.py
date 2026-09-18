import json
import os

ARCHIVO = "save_data.json"

def cargar():
    """Carga el progreso. Si no hay partida, inicia en la Fase 1."""
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, "r") as f:
            return json.load(f)
    return {"fase_desbloqueada": 1}

def guardar(fase):
    """Guarda el progreso asegurando que no se pueda 'des-avanzar'."""
    datos = cargar()
    if fase > datos.get("fase_desbloqueada", 1):
        datos["fase_desbloqueada"] = fase
        
    with open(ARCHIVO, "w") as f:
        json.dump(datos, f)