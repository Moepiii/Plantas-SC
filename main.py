#librerias rarongas
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
import logging

# Estados para ConversationHandlers
ELEGIR_PLANTA, INGRESAR_MEDIDA = range(2)
ELEGIR_PLANTA_ESTATURA = 3

# Diccionarios para almacenar datos por usuario
plantas_por_usuario = {}
medidas_por_usuario = {}

# Logging
logging.basicConfig(level=logging.INFO)

# /start mensaje de bienvenida podemos mejorarlo maybe...
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

# /registrar registra plantas... super
async def registrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("❗ Usa: /registrar <nombre_de_la_planta>")
        return
    nombre_planta = " ".join(context.args)
    plantas_por_usuario.setdefault(user_id, []).append(nombre_planta)
    await update.message.reply_text(f"✅ Planta '{nombre_planta}' registrada.")

# /verplantas ves las que tienes daaaa
async def ver_plantas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    plantas = plantas_por_usuario.get(user_id, [])
    if not plantas:
        await update.message.reply_text("🌱 No tienes plantas registradas aún.")
    else:
        lista = "\n".join(f"- {p}" for p in plantas)
        await update.message.reply_text(f"🌿 Tus plantas:\n{lista}")

# /eliminar no fiodor baja a tu marioneta
async def eliminar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("❗ Usa: /eliminar <nombre_de_la_planta>")
        return
    nombre = " ".join(context.args)
    if nombre in plantas_por_usuario.get(user_id, []):
        plantas_por_usuario[user_id].remove(nombre)
        await update.message.reply_text(f"🗑️ '{nombre}' eliminada.")
    else:
        await update.message.reply_text(f"⚠️ Planta '{nombre}' no encontrada.")

# /medir iiihh 4 horas + onli
async def medir_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    plantas = plantas_por_usuario.get(user_id, [])
    if not plantas:
        await update.message.reply_text("❌ No tienes plantas registradas para medir.")
        return ConversationHandler.END

    teclado = [[p] for p in plantas]
    reply_markup = ReplyKeyboardMarkup(teclado, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🌿 Elige la planta que quieres medir:", reply_markup=reply_markup)
    return ELEGIR_PLANTA

async def medir_elegir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    planta = update.message.text
    user_id = update.effective_user.id

    if planta not in plantas_por_usuario.get(user_id, []):
        await update.message.reply_text("⚠️ Esa planta no está en tu lista.")
        return ConversationHandler.END

    context.user_data["planta_seleccionada"] = planta
    await update.message.reply_text("📏 Ingresa la medida (ejemplo: 23.5 cm):", reply_markup=ReplyKeyboardRemove())
    return INGRESAR_MEDIDA

async def medir_guardar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    medida = update.message.text
    user_id = update.effective_user.id
    planta = context.user_data["planta_seleccionada"]

    medidas_por_usuario.setdefault(user_id, {})
    medidas_por_usuario[user_id].setdefault(planta, []).append(medida)

    await update.message.reply_text(f"✅ Medida '{medida}' registrada para '{planta}'.")
    return ConversationHandler.END

# /estatura se deben acomdar cosas
async def estatura_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    plantas = plantas_por_usuario.get(user_id, [])

    if not plantas:
        await update.message.reply_text("🌱 No tienes plantas registradas.")
        return ConversationHandler.END

    teclado = [[p] for p in plantas]
    reply_markup = ReplyKeyboardMarkup(teclado, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🔍 ¿De qué planta quieres ver la última estatura?", reply_markup=reply_markup)
    return ELEGIR_PLANTA_ESTATURA

async def estatura_respuesta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    planta = update.message.text
    user_id = update.effective_user.id

    if planta not in plantas_por_usuario.get(user_id, []):
        await update.message.reply_text("⚠️ Esa planta no está registrada.")
        return ConversationHandler.END

    medidas = medidas_por_usuario.get(user_id, {}).get(planta, [])
    if not medidas:
        await update.message.reply_text(f"📏 La planta '{planta}' aún no tiene medidas registradas.")
    else:
        ultima = medidas[-1]
        await update.message.reply_text(f"🌿 La última estatura registrada de '{planta}' es: {ultima}")

    return ConversationHandler.END

# /cancelar
async def medir_cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Acción cancelada.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Crear la aplicación
app = ApplicationBuilder().token("8059185234:AAHEY0JEB_liE7_h2soULyowz_xArACKmJE").build()

# Handlers básicos
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("registrar", registrar))
app.add_handler(CommandHandler("verplantas", ver_plantas))
app.add_handler(CommandHandler("eliminar", eliminar))

# Conversación para /medir
medir_handler = ConversationHandler(
    entry_points=[CommandHandler("medir", medir_inicio)],
    states={
        ELEGIR_PLANTA: [MessageHandler(filters.TEXT & ~filters.COMMAND, medir_elegir)],
        INGRESAR_MEDIDA: [MessageHandler(filters.TEXT & ~filters.COMMAND, medir_guardar)],
    },
    fallbacks=[CommandHandler("cancelar", medir_cancelar)],
)
app.add_handler(medir_handler)

# Conversación para /estatura
estatura_handler = ConversationHandler(
    entry_points=[CommandHandler("estatura", estatura_inicio)],
    states={
        ELEGIR_PLANTA_ESTATURA: [MessageHandler(filters.TEXT & ~filters.COMMAND, estatura_respuesta)],
    },
    fallbacks=[CommandHandler("cancelar", medir_cancelar)],
)
app.add_handler(estatura_handler)

# Ejecutar el bot
app.run_polling(allowed_updates=Update.ALL_TYPES)

