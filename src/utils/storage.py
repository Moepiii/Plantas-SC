import json
import os

from src.config import Config

# Constante para horas totales de servicio comunitario
TOTAL_HORAS = Config.TOTAL_HORAS_SERVICIO

# Diccionarios globales para almacenar datos
plantas_por_usuario = {}
medidas_por_usuario = {}
riego_por_usuario = {}
horas_por_usuario = {}

def obtener_ruta_archivo(nombre_archivo):
    """Obtiene la ruta completa del archivo de datos"""
    return os.path.join(Config.DATA_DIR, nombre_archivo)

def cargar_datos():
    """Carga todos los datos desde archivos JSON"""
    global plantas_por_usuario, medidas_por_usuario, riego_por_usuario, horas_por_usuario
    
    # Crear directorio de datos si no existe
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    
    # Cargar plantas
    try:
        with open(obtener_ruta_archivo('plantas.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
            plantas_por_usuario.update({int(k): v for k, v in data.items()})
    except (FileNotFoundError, json.JSONDecodeError):
        plantas_por_usuario.clear()
    
    # Cargar medidas
    try:
        with open(obtener_ruta_archivo('medidas.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
            medidas_por_usuario.update({int(k): v for k, v in data.items()})
    except (FileNotFoundError, json.JSONDecodeError):
        medidas_por_usuario.clear()
    
    # Cargar riego
    try:
        with open(obtener_ruta_archivo('riego.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
            riego_por_usuario.update({int(k): v for k, v in data.items()})
    except (FileNotFoundError, json.JSONDecodeError):
        riego_por_usuario.clear()
    
    # Cargar horas
    try:
        with open(obtener_ruta_archivo('horas.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
            horas_por_usuario.update({int(k): v for k, v in data.items()})
    except (FileNotFoundError, json.JSONDecodeError):
        horas_por_usuario.clear()

def guardar_datos():
    """Guarda todos los datos en archivos JSON"""
    # Crear directorio si no existe
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    
    # Guardar plantas
    try:
        with open(obtener_ruta_archivo('plantas.json'), 'w', encoding='utf-8') as f:
            json.dump(plantas_por_usuario, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error guardando plantas: {e}")
    
    # Guardar medidas
    try:
        with open(obtener_ruta_archivo('medidas.json'), 'w', encoding='utf-8') as f:
            json.dump(medidas_por_usuario, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error guardando medidas: {e}")
    
    # Guardar riego
    try:
        with open(obtener_ruta_archivo('riego.json'), 'w', encoding='utf-8') as f:
            json.dump(riego_por_usuario, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error guardando riego: {e}")
    
    # Guardar horas
    try:
        with open(obtener_ruta_archivo('horas.json'), 'w', encoding='utf-8') as f:
            json.dump(horas_por_usuario, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error guardando horas: {e}")

def obtener_estadisticas():
    """Obtiene estadísticas generales del bot"""
    total_usuarios = len(set(list(plantas_por_usuario.keys()) + 
                            list(horas_por_usuario.keys()) + 
                            list(riego_por_usuario.keys()) + 
                            list(medidas_por_usuario.keys())))
    
    total_plantas = sum(len(plantas) for plantas in plantas_por_usuario.values())
    total_medidas = sum(len(medidas) for medidas_dict in medidas_por_usuario.values() 
                       for medidas in medidas_dict.values())
    
    return {
        "total_usuarios": total_usuarios,
        "total_plantas": total_plantas,
        "total_medidas": total_medidas,
        "usuarios_con_plantas": len(plantas_por_usuario),
        "usuarios_con_horas": len(horas_por_usuario)
    }