from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import logging

# Activar logging por si ocurre un error
logging.basicConfig(level=logging.INFO)

# Diccionario para guardar plantas por usuario
plantas_por_usuario = {}

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = (
        "🌿 ¡Bienvenido al Bot de Control de Plantas! 🌱\n\n"
        "Puedes usar los siguientes comandos:\n"
        "/registrar - Registrar una nueva planta\n"
        "/verplantas - Ver tus plantas registradas\n"
    )
    await update.message.reply_text(mensaje)

# Comando /registrar
async def registrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Verificamos que el usuario haya enviado el nombre de la planta
    if not context.args:
        await update.message.reply_text("❗ Usa el comando así: /registrar <nombre_de_la_planta>")
        return

    nombre_planta = " ".join(context.args)

    # Guardar planta en la lista del usuario
    if user_id not in plantas_por_usuario:
        plantas_por_usuario[user_id] = []

    plantas_por_usuario[user_id].append(nombre_planta)

    await update.message.reply_text(f"✅ Planta '{nombre_planta}' registrada correctamente.")

# Comando /verplantas
async def ver_plantas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    plantas = plantas_por_usuario.get(user_id, [])

    if not plantas:
        await update.message.reply_text("🌱 No tienes plantas registradas aún.")
    else:
        lista = "\n".join(f"- {planta}" for planta in plantas)
        await update.message.reply_text(f"🌿 Tus plantas registradas:\n{lista}")

# Construcción de la aplicación
app = ApplicationBuilder().token("8059185234:AAHEY0JEB_liE7_h2soULyowz_xArACKmJE").build()

# Agregar manejadores
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("registrar", registrar))
app.add_handler(CommandHandler("verplantas", ver_plantas))

# Ejecutar el bot
app.run_polling(allowed_updates=Update.ALL_TYPES)



