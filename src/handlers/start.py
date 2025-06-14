from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

GIF_URL = "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExM29mbmY0d3lvZXl3ZGo3ZWV5cWtxOTcxZ24xdDR0dmhxZThmeHB2eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/d9Hhu2N1KTF0uW76WQ/giphy.gif"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = (
        "🌿 ¡Bienvenido al Bot de Control de Plantas! 🌱\n\n"
        "Acciones generales que puedes realizar:\n"
        "1️⃣ Consulta tus plantitas\n"
        "2️⃣ Crecimiento de plantas\n"
        "3️⃣ Riego de plantas\n"
        "4️⃣ Seguimiento de horas del SC\n"
        "5️⃣ Otros comandos\n\n"
        "Para ver la lista de comandos y detalles, usa /help\n"
        "Para ayuda específica de una sección, usa /help <número>"
    )
    await update.message.reply_animation(GIF_URL)
    await update.message.reply_text(mensaje)

start_handler = CommandHandler("start", start)