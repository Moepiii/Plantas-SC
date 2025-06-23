from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

HELP_SECTIONS = {
    "1": (
        "🍃 *Consulta tus plantitas* 🍃\n"
        "   /verplantas - Ver tus plantas registradas\n"
        "   /registrar <nombre> - Registrar una nueva planta\n"
        "   /eliminar <nombre> - Eliminar una planta\n"
    ),
    "2": (
        "🌱 *Crecimiento de plantas* 🌱\n"
        "   /medir - Medir una planta\n"
        "   /estatura - Ver la última medida de una planta\n"
        "   /eliminar\\_medida - Elimina medidas de plantas\n"
    ),
    "3": (
        "💧 *Riego de plantas* 💧\n"
        "   /regar <nombre> <días> - Configurar frecuencia y registrar riego de una planta\n"
        "   /consultarRiego <nombre> - Consultar frecuencia y último riego de una planta\n"
        "   /cambiarRiego <nombre> <YYYY-MM-DD> - Cambiar la fecha del último riego\n"
        "   /cambiarFrecuencia <nombre> <días> - Cambiar la frecuencia de riego\n"
    ),
    "4": (
        "🕒 *Seguimiento de horas de Servicio Comunitario* 🕒\n"
        "   /registrarHorasDeHoy <horas> - Registrar horas para hoy\n"
        "   /registrarHorasConFecha <horas> <YYYY-MM-DD> - Registrar horas en otra fecha\n"
        "   /horasCumplidas - Ver resumen de horas cumplidas\n"
        "   /eliminarHoras <horas> <YYYY-MM-DD> - Eliminar horas de una fecha\n"
    ),
    "5": (
        "🔧 *Otros comandos* 🔧\n"
        "   /cancelar - Cancelar cualquier acción\n"
        "   /start - Muestra las acciones generales\n"
        "   /help - Muestra este mensaje de ayuda\n"
        "   /borrarMisDatos - Elimina todos tus datos del bot\n"
    )
}

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        mensaje = (
            "ℹ️ *Ayuda general*\n\n"
            "1️⃣ Consulta tus plantitas\n"
            "2️⃣ Crecimiento de plantas\n"
            "3️⃣ Riego de plantas\n"
            "4️⃣ Seguimiento de horas del SC\n"
            "5️⃣ Otros comandos\n\n"
            "Para ayuda específica de una sección, usa /help <número>\n\n"
        )
        for i in ["1", "2", "3", "4", "5"]:
            mensaje += HELP_SECTIONS[i] + "\n"
        await update.message.reply_text(mensaje, parse_mode="Markdown")
        return

    seccion = args[0]
    if seccion in HELP_SECTIONS:
        mensaje = HELP_SECTIONS[seccion]
        await update.message.reply_text(mensaje, parse_mode="Markdown")
    else:
        await update.message.reply_text("Sección no encontrada. Usa /help para ver las opciones.", parse_mode="Markdown")

help_handler = CommandHandler("help", help_command)