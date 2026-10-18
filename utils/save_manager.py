import json
import os
import uuid
import sys
from utils.supabase_manager import upsert_session_async

# Usar ruta absoluta basada en la ubicación del script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVO = os.path.join(BASE_DIR, "save_data.json")

def _es_web():
    return sys.platform == "emscripten"

def cargar():
    datos = {"fase_desbloqueada": 1, "secretos": [], "autenticado": False, "config": {"musica": 1.0, "sfx": 1.0}}
    
    if _es_web():
        from platform import window
        raw = window.localStorage.getItem("protocolo_brecha_save")
        if raw:
            try:
                datos.update(json.loads(raw))
            except:
                pass
    elif os.path.exists(ARCHIVO):
        try:
            with open(ARCHIVO, "r") as f:
                datos.update(json.load(f))
        except Exception as e:
            print(f"Error al cargar partida: {e}. Se usará una partida nueva.")
            
    if "secretos" not in datos: datos["secretos"] = []
    if "autenticado" not in datos: datos["autenticado"] = False
    if "config" not in datos: datos["config"] = {"musica": 1.0, "sfx": 1.0}
    if "session_id" not in datos: datos["session_id"] = str(uuid.uuid4())
    if "times" not in datos: datos["times"] = {"total": 0.0, "100_percent": 0.0, "phases": {}}
    if "answers" not in datos: datos["answers"] = {"q1": "", "q2": "", "q3": "", "final": ""}
    
    return datos

def reiniciar_partida(mantener_config=True):
    datos = cargar()
    config_audio = datos.get("config", {"musica": 1.0, "sfx": 1.0}) if mantener_config else {"musica": 1.0, "sfx": 1.0}
    session_id = datos.get("session_id", str(uuid.uuid4()))
    datos_nuevos = {
        "fase_desbloqueada": 1,
        "secretos": [],
        "autenticado": True,
        "config": config_audio,
        "session_id": session_id,
        "times": {"total": 0.0, "100_percent": 0.0, "phases": {}},
        "answers": {"q1": "", "q2": "", "q3": "", "final": ""}
    }
    if _es_web():
        from platform import window
        window.localStorage.setItem("protocolo_brecha_save", json.dumps(datos_nuevos))
    else:
        try:
            with open(ARCHIVO, "w") as f:
                json.dump(datos_nuevos, f, indent=4)
        except Exception as e:
            print(f"Error al reiniciar partida: {e}")
    upsert_session_async(datos_nuevos)
    return datos_nuevos

def guardar(fase=None, secreto=None, autenticado=None, config_audio=None, answer_key=None, answer_val=None, phase_name=None, phase_time_add=0.0, total_time_add=0.0, forzar_fase=False):
    datos = cargar()
    
    if fase is not None:
        if forzar_fase or fase > datos.get("fase_desbloqueada", 1):
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
        
    if answer_key is not None and answer_val is not None:
        datos["answers"][answer_key] = answer_val
        
    if phase_name is not None:
        if phase_name not in datos["times"]["phases"]:
            datos["times"]["phases"][phase_name] = 0.0
        datos["times"]["phases"][phase_name] += phase_time_add
        
    if total_time_add > 0:
        datos["times"]["total"] += total_time_add
        
    # Check 100% completion
    if len(datos["secretos"]) >= 9 and datos["times"]["100_percent"] == 0.0:
        datos["times"]["100_percent"] = datos["times"]["total"]
            
    if _es_web():
        from platform import window
        window.localStorage.setItem("protocolo_brecha_save", json.dumps(datos))
    else:
        try:
            with open(ARCHIVO, "w") as f:
                json.dump(datos, f, indent=4)
        except Exception as e:
            print(f"Error al guardar partida: {e}")
        
    # Sincronizar con Supabase
    upsert_session_async(datos)