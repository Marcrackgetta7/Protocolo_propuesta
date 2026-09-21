import json
import os

# Usar ruta absoluta basada en la ubicación del script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVO = os.path.join(BASE_DIR, "save_data.json")

def cargar():
    if os.path.exists(ARCHIVO):
        try:
            with open(ARCHIVO, "r") as f:
                datos = json.load(f)
                if "secretos" not in datos: datos["secretos"] = []
                if "autenticado" not in datos: datos["autenticado"] = False
                if "config" not in datos: datos["config"] = {"musica": 1.0, "sfx": 1.0}
                return datos
        except Exception as e:
            print(f"Error al cargar partida: {e}. Se usará una partida nueva.")
            
    return {"fase_desbloqueada": 1, "secretos": [], "autenticado": False, "config": {"musica": 1.0, "sfx": 1.0}}

def guardar(fase=None, secreto=None, autenticado=None, config_audio=None):
    datos = cargar()
    
    if fase is not None and fase > datos.get("fase_desbloqueada", 1):
        datos["fase_desbloqueada"] = fase
        
    if secreto is not None:
        if secreto not in datos["secretos"]:
            datos["secretos"].append(secreto)
            from utils.toast import ToastManager
            ToastManager.get().mostrar("¡ARCHIVO OCULTO DESBLOQUEADO!", secreto)
            
    if autenticado is not None:
        datos["autenticado"] = autenticado
        
    if config_audio is not None:
        datos["config"] = config_audio
            
    try:
        with open(ARCHIVO, "w") as f:
            json.dump(datos, f)
    except Exception as e:
        print(f"Error al guardar partida: {e}")