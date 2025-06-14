import logging
from telegram import Update
from telegram.ext import ApplicationBuilder
from src.handlers.start import start_handler
from src.handlers.register import registrar_handler
from src.handlers.view_plants import verplantas_handler
from src.handlers.delete import eliminar_handler
from src.handlers.measure import medir_handler
from src.handlers.high import estatura_handler
from src.handlers.reminder import revisar_riegos
from src.handlers.water import regar_handler
from src.handlers.change_frequency import cambiar_frecuencia_handler
from src.handlers.change_watering import cambiar_riego_handler
from src.handlers.consult_watering import consultar_riego_handler
from src.utils.storage import cargar_datos

# Configuración de logging
logging.basicConfig(level=logging.INFO)

def run_bot():
    cargar_datos()
    app = ApplicationBuilder().token("8059185234:AAHEY0JEB_liE7_h2soULyowz_xArACKmJE").build()
    app.add_handler(start_handler)
    app.add_handler(registrar_handler)
    app.add_handler(verplantas_handler)
    app.add_handler(eliminar_handler)
    app.add_handler(medir_handler)
    app.add_handler(estatura_handler)
    app.add_handler(regar_handler)

    app.add_handler(cambiar_frecuencia_handler)
    app.add_handler(cambiar_riego_handler)
    app.add_handler(consultar_riego_handler)
    app.job_queue.run_repeating(revisar_riegos, interval=60, first=10)  # Cada minuto
    app.run_polling(allowed_updates=Update.ALL_TYPES)