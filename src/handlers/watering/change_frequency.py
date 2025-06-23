from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from src.utils.storage import plantas_por_usuario, riego_por_usuario, guardar_datos

async def cambiar_frecuencia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if len(context.args) < 2:
        await update.message.reply_text("❗ Usa: /cambiarFrecuencia <nombre_de_la_planta> <nueva_frecuencia_en_dias>")
        return

    nombre_planta = " ".join(context.args[:-1]).strip()
    frecuencia_str = context.args[-1]

    # Verifica que la planta esté registrada
    if user_id not in plantas_por_usuario or nombre_planta not in plantas_por_usuario[user_id]:
        await update.message.reply_text(f"⚠️ La planta '{nombre_planta}' no está registrada.")
        return

    # Verifica que la planta tenga frecuencia de riego registrada
    if user_id not in riego_por_usuario or nombre_planta not in riego_por_usuario[user_id]:
        await update.message.reply_text(f"ℹ️ No hay frecuencia de riego registrada para '{nombre_planta}'. Usa /regar para configurarla.")
        return

    # Valida la frecuencia
    try:
        frecuencia = int(frecuencia_str)
        if frecuencia <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❗ La frecuencia debe ser un número entero mayor a 0.")
        return

    riego_por_usuario[user_id][nombre_planta]["frecuencia"] = frecuencia
    guardar_datos()
    await update.message.reply_text(
        f"✅ Frecuencia de riego de '{nombre_planta}' actualizada a cada {frecuencia} días."
    )

cambiar_frecuencia_handler = CommandHandler("cambiarFrecuencia", cambiar_frecuencia)