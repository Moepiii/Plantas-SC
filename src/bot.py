import logging
from telegram import Update
from telegram.ext import ApplicationBuilder
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
from src.handlers.hours.register_hours_today import registrar_horas_de_hoy_handler
from src.handlers.hours.register_hours_with_date import registrar_horas_con_fecha_handler
from src.handlers.hours.hours_summary import horas_cumplidas_handler
from src.handlers.hours.delete_hours import eliminar_horas_handler

from src.handlers.reminder import revisar_riegos
from src.utils.storage import cargar_datos

# Configuración de logging
logging.basicConfig(level=logging.INFO)

def run_bot():
    cargar_datos()
    app = ApplicationBuilder().token("8059185234:AAHEY0JEB_liE7_h2soULyowz_xArACKmJE").build()
    app.add_handler(start_handler)
    app.add_handler(help_handler)
    app.add_handler(borrar_mis_datos_handler)
    # Plantas
    app.add_handler(registrar_handler)
    app.add_handler(verplantas_handler)
    app.add_handler(eliminar_handler)
    # Crecimiento
    app.add_handler(medir_handler)
    app.add_handler(estatura_handler)
    app.add_handler(eliminar_medida_handler)
    # Riego
    app.add_handler(regar_handler)
    app.add_handler(consultar_riego_handler)
    app.add_handler(cambiar_riego_handler)
    app.add_handler(cambiar_frecuencia_handler)
    # Horas
    app.add_handler(registrar_horas_de_hoy_handler)
    app.add_handler(registrar_horas_con_fecha_handler)
    app.add_handler(horas_cumplidas_handler)
    app.add_handler(eliminar_horas_handler)
    # Recordatorio de riego
    app.job_queue.run_repeating(revisar_riegos, interval=60, first=10) # Cada minuto
    app.run_polling(allowed_updates=Update.ALL_TYPES)