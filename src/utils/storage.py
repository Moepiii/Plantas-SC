import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

PLANTAS_FILE = os.path.join(DATA_DIR, "plantas.json")
MEDIDAS_FILE = os.path.join(DATA_DIR, "medidas.json")

# Diccionarios globales para almacenar datos por usuario

plantas_por_usuario = {}
medidas_por_usuario = {}

def cargar_datos():
    global plantas_por_usuario, medidas_por_usuario
    if os.path.exists(PLANTAS_FILE):
        with open(PLANTAS_FILE, "r") as f:
            data = json.load(f)
            plantas_por_usuario.clear()
            plantas_por_usuario.update({int(k): v for k, v in data.items()})
    if os.path.exists(MEDIDAS_FILE):
        with open(MEDIDAS_FILE, "r") as f:
            data = json.load(f)
            medidas_por_usuario.clear()
            medidas_por_usuario.update({int(k): v for k, v in data.items()})

def guardar_datos():
    with open(PLANTAS_FILE, "w") as f:
        json.dump(plantas_por_usuario, f)
    with open(MEDIDAS_FILE, "w") as f:
        json.dump(medidas_por_usuario, f)