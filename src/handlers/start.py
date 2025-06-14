from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = (
        "🌿 ¡Bienvenido al Bot de Control de Plantas! 🌱\n\n"
        "Comandos disponibles:\n"
        "/registrar <nombre> - Registrar una nueva planta\n"
        "/verplantas - Ver tus plantas registradas\n"
        "/eliminar <nombre> - Eliminar una planta\n"
        "/medir - Medir una planta\n"
        "/estatura - Ver la última medida de una planta\n"
        "/cancelar - Cancelar cualquier acción\n"
    )
    await update.message.reply_text(mensaje)

start_handler = CommandHandler("start", start)