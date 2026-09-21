import json
import os

ARCHIVO = "save_data.json"

def cargar():
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, "r") as f:
            datos = json.load(f)
            if "secretos" not in datos: 
                datos["secretos"] = []
            if "autenticado" not in datos:
                datos["autenticado"] = False
            return datos
    return {"fase_desbloqueada": 1, "secretos": [], "autenticado": False}

def guardar(fase=None, secreto=None, autenticado=None):
    datos = cargar()
    
    if fase is not None and fase > datos.get("fase_desbloqueada", 1):
        datos["fase_desbloqueada"] = fase
        
    if secreto is not None:
        if secreto not in datos["secretos"]:
            datos["secretos"].append(secreto)
            
    if autenticado is not None:
        datos["autenticado"] = autenticado
            
    with open(ARCHIVO, "w") as f:
        json.dump(datos, f)