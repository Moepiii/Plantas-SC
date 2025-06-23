from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from src.utils.storage import plantas_por_usuario, riego_por_usuario

async def consultar_riego(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text("❗ Usa: /consultarRiego <nombre_de_la_planta>")
        return

    nombre_planta = " ".join(context.args).strip()

    # Verifica que la planta esté registrada
    if user_id not in plantas_por_usuario or nombre_planta not in plantas_por_usuario[user_id]:
        await update.message.reply_text(f"⚠️ La planta '{nombre_planta}' no está registrada.")
        return

    datos_riego = riego_por_usuario.get(user_id, {}).get(nombre_planta)
    if not datos_riego:
        await update.message.reply_text(f"ℹ️ No hay frecuencia de riego registrada para '{nombre_planta}'. Usa /regar para configurarla.")
        return

    frecuencia = datos_riego["frecuencia"]
    ultimo_riego = datos_riego["ultimo_riego"]
    await update.message.reply_text(
        f"💧 Frecuencia de riego para '{nombre_planta}': cada {frecuencia} días.\n"
        f"Último riego registrado: {ultimo_riego}"
    )

consultar_riego_handler = CommandHandler("consultarRiego", consultar_riego)