from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes
)
from src.utils.storage import plantas_por_usuario, medidas_por_usuario

ELEGIR_PLANTA_ESTATURA = 3

async def estatura_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    plantas = [p for p in plantas_por_usuario.get(user_id, []) if p.strip()]

    if not plantas:
        await update.message.reply_text("🌱 No tienes plantas registradas.")
        return ConversationHandler.END

    teclado = [[p] for p in plantas]
    reply_markup = ReplyKeyboardMarkup(teclado, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🔍 ¿De qué planta quieres ver la última estatura?", reply_markup=reply_markup)
    return ELEGIR_PLANTA_ESTATURA

async def estatura_respuesta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    planta_input = update.message.text.strip()
    user_id = update.effective_user.id
    plantas = [p for p in plantas_por_usuario.get(user_id, []) if p.strip()]

    # Normaliza para comparar
    planta = next((p for p in plantas if p.lower() == planta_input.lower()), None)

    if not planta:
        await update.message.reply_text("⚠️ Esa planta no está registrada. Usa el teclado para seleccionar.")
        return ConversationHandler.END

    medidas = medidas_por_usuario.get(user_id, {}).get(planta, [])
    if not medidas:
        await update.message.reply_text(f"📏 La planta '{planta}' aún no tiene medidas registradas.")
    else:
        ultima = medidas[-1]
        await update.message.reply_text(f"🌿 La última estatura registrada de '{planta}' es: {ultima} cm")

    return ConversationHandler.END

async def medir_cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Acción cancelada.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

estatura_handler = ConversationHandler(
    entry_points=[CommandHandler("estatura", estatura_inicio)],
    states={
        ELEGIR_PLANTA_ESTATURA: [MessageHandler(filters.TEXT & ~filters.COMMAND, estatura_respuesta)],
    },
    fallbacks=[CommandHandler("cancelar", medir_cancelar)],
)