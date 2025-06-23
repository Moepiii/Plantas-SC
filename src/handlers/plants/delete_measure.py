from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes
)
from src.utils.storage import plantas_por_usuario, medidas_por_usuario, guardar_datos

ELEGIR_PLANTA, ELEGIR_MEDIDA = range(2)

async def eliminar_medida_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    plantas = [p for p in plantas_por_usuario.get(user_id, []) if p.strip()]
    if not plantas:
        await update.message.reply_text("❌ No tienes plantas registradas.")
        return ConversationHandler.END

    teclado = [[p] for p in plantas]
    reply_markup = ReplyKeyboardMarkup(teclado, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🌿 Elige la planta de la que quieres eliminar una medida:", reply_markup=reply_markup)
    return ELEGIR_PLANTA

async def eliminar_medida_elegir_planta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    planta = update.message.text.strip()
    user_id = update.effective_user.id

    if planta not in plantas_por_usuario.get(user_id, []):
        await update.message.reply_text("⚠️ Esa planta no está en tu lista.")
        return ConversationHandler.END

    medidas = medidas_por_usuario.get(user_id, {}).get(planta, [])
    if not medidas:
        await update.message.reply_text(f"📏 La planta '{planta}' no tiene medidas registradas.")
        return ConversationHandler.END

    context.user_data["planta_seleccionada"] = planta
    # Mostrar las medidas con índices
    medidas_lista = "\n".join([f"{i+1}. {m} cm" for i, m in enumerate(medidas)])
    await update.message.reply_text(
        f"Estas son las medidas registradas para '{planta}':\n{medidas_lista}\n\n"
        "Escribe el número de la medida que deseas eliminar.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ELEGIR_MEDIDA

async def eliminar_medida_confirmar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    planta = context.user_data.get("planta_seleccionada")
    medidas = medidas_por_usuario.get(user_id, {}).get(planta, [])

    try:
        indice = int(update.message.text.strip()) - 1
        if indice < 0 or indice >= len(medidas):
            raise ValueError
    except ValueError:
        await update.message.reply_text("❗ Ingresa un número válido de la lista.")
        return ELEGIR_MEDIDA

    medida_eliminada = medidas.pop(indice)
    guardar_datos()

    await update.message.reply_text(
        f"✅ Medida '{medida_eliminada} cm' eliminada de '{planta}'.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def eliminar_medida_cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Acción cancelada.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

eliminar_medida_handler = ConversationHandler(
    entry_points=[CommandHandler("eliminar_medida", eliminar_medida_inicio)],
    states={
        ELEGIR_PLANTA: [MessageHandler(filters.TEXT & ~filters.COMMAND, eliminar_medida_elegir_planta)],
        ELEGIR_MEDIDA: [MessageHandler(filters.TEXT & ~filters.COMMAND, eliminar_medida_confirmar)],
    },
    fallbacks=[CommandHandler("cancelar", eliminar_medida_cancelar)],
)
