from telegram.ext import ApplicationBuilder
from src.config import Config
from src.utils.logger import setup_logger
from src.utils.storage import cargar_datos

# Importar todos los handlers con decoradores mejorados
from src.handlers.start import start_handler
from src.handlers.help import help_handler
from src.handlers.start import start_handler
from src.handlers.help import help_handler
from src.handlers.delete_my_data import borrar_mis_datos_handler

# Plantas
from src.handlers.plants.register import registrar_handler
from src.handlers.plants.view_plants import verplantas_handler
from src.handlers.plants.delete import eliminar_handler

# Crecimiento
from src.handlers.plants.measure import medir_handler
from src.handlers.plants.high import estatura_handler
from src.handlers.plants.delete_measure import eliminar_medida_handler

# Riego
from src.handlers.watering.water import regar_handler
from src.handlers.watering.consult_watering import consultar_riego_handler
from src.handlers.watering.change_watering import cambiar_riego_handler
from src.handlers.watering.change_frequency import cambiar_frecuencia_handler

# Horas
from src.handlers.hours.register_hours_today import register_hours_today_handler
from src.handlers.hours.register_hours_with_date import registrar_horas_con_fecha_handler
from src.handlers.hours.hours_summary import horas_cumplidas_handler
from src.handlers.hours.delete_hours import eliminar_horas_handler

from src.handlers.reminder import revisar_riegos
from src.utils.storage import cargar_datos

def run_bot():
    """Función principal mejorada para ejecutar el bot"""
    
    # Configurar logging
    logger = setup_logger()
    
    try:
        # Validar configuración
        Config.validate()
        logger.info("Configuración validada correctamente")
        
        # Cargar datos persistentes
        cargar_datos()
        logger.info("Datos cargados desde archivos JSON")
        
        # Crear aplicación del bot
        app = ApplicationBuilder().token(Config.BOT_TOKEN).build()
        
        # Registrar todos los handlers
        handlers = [
            start_handler, help_handler, borrar_mis_datos_handler,
            # Plantas
            registrar_handler, verplantas_handler, eliminar_handler,
            # Crecimiento
            medir_handler, estatura_handler, eliminar_medida_handler,
            # Riego
            regar_handler, consultar_riego_handler, cambiar_riego_handler,
            cambiar_frecuencia_handler,
            # Horas
            register_hours_today_handler, registrar_horas_con_fecha_handler,
            horas_cumplidas_handler, eliminar_horas_handler
        ]
        
        for handler in handlers:
            app.add_handler(handler)
        
        logger.info(f"Registrados {len(handlers)} handlers")
        
        # Agregar job de recordatorio de riego (cada minuto)
        app.job_queue.run_repeating(revisar_riegos, interval=60, first=10)
        
        logger.info("Bot iniciado correctamente")
        print("🤖 Bot Plantas-SC está funcionando...")
        print("Presiona Ctrl+C para detener")
        
        # Ejecutar bot
        app.run_polling(allowed_updates=["message"])
        
    except Exception as e:
        logger.error(f"Error crítico al iniciar el bot: {str(e)}")
        raise

if __name__ == "__main__":
    run_bot()