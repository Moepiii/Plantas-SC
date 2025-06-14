from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = (
        "🌿 ¡Bienvenido al Bot de Control de Plantas! 🌱\n\n"
        "🍃 *Consulta tus plantitas*\n"
        "  /verplantas - Ver tus plantas registradas\n"
        "  /registrar <nombre> - Registrar una nueva planta\n"
        "  /eliminar <nombre> - Eliminar una planta\n\n"
        "🌱 *Crecimiento de plantas*\n"
        "  /medir - Medir una planta\n"
        "  /estatura - Ver la última medida de una planta\n\n"
        "💧 *Riego de plantas*\n"
        "  /regar <nombre> <días> - Configurar frecuencia y registrar riego de una planta\n"
        "  /consultarRiego <nombre> - Consultar frecuencia y último riego de una planta\n"
        "  /cambiarRiego <nombre> <YYYY-MM-DD> - Cambiar la fecha del último riego\n"
        "  /cambiarFrecuencia <nombre> <días> - Cambiar la frecuencia de riego\n\n"
        "❌ /cancelar - Cancelar cualquier acción\n"
    )
    await update.message.reply_text(mensaje, parse_mode="Markdown")

start_handler = CommandHandler("start", start)