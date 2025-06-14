from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes
)
from src.utils.storage import plantas_por_usuario, medidas_por_usuario, guardar_datos

ELEGIR_PLANTA, INGRESAR_MEDIDA = range(2)

async def medir_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    plantas = [p for p in plantas_por_usuario.get(user_id, []) if p.strip()]
    if not plantas:
        await update.message.reply_text("❌ No tienes plantas registradas para medir.")
        return ConversationHandler.END

    teclado = [[p] for p in plantas]
    reply_markup = ReplyKeyboardMarkup(teclado, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🌿 Elige la planta que quieres medir:", reply_markup=reply_markup)
    return ELEGIR_PLANTA

async def medir_elegir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    planta = update.message.text.strip()
    user_id = update.effective_user.id

    if planta not in plantas_por_usuario.get(user_id, []):
        await update.message.reply_text("⚠️ Esa planta no está en tu lista.")
        return ConversationHandler.END

    context.user_data["planta_seleccionada"] = planta
    await update.message.reply_text("📏 Ingresa la medida en centímetros (solo el número, ejemplo: 23.5):", reply_markup=ReplyKeyboardRemove())
    return INGRESAR_MEDIDA

async def medir_guardar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    medida = update.message.text.strip()
    user_id = update.effective_user.id
    planta = context.user_data.get("planta_seleccionada")

    try:
        valor = float(medida.replace(",", "."))
    except ValueError:
        await update.message.reply_text("❗ Ingresa solo el número de la medida en centímetros (ejemplo: 23.5).")
        return INGRESAR_MEDIDA

    medidas_por_usuario.setdefault(user_id, {})
    medidas_por_usuario[user_id].setdefault(planta, []).append(valor)
    guardar_datos()

    await update.message.reply_text(f"✅ Medida '{valor} cm' registrada para '{planta}'.")
    return ConversationHandler.END

async def medir_cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Acción cancelada.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

medir_handler = ConversationHandler(
    entry_points=[CommandHandler("medir", medir_inicio)],
    states={
        ELEGIR_PLANTA: [MessageHandler(filters.TEXT & ~filters.COMMAND, medir_elegir)],
        INGRESAR_MEDIDA: [MessageHandler(filters.TEXT & ~filters.COMMAND, medir_guardar)],
    },
    fallbacks=[CommandHandler("cancelar", medir_cancelar)],
)