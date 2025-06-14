from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from datetime import datetime
from src.utils.storage import plantas_por_usuario, riego_por_usuario, guardar_datos

async def cambiar_riego(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if len(context.args) < 2:
        await update.message.reply_text("❗ Usa: /cambiarRiego <nombre_de_la_planta> <YYYY-MM-DD>")
        return

    nombre_planta = " ".join(context.args[:-1]).strip()
    fecha_str = context.args[-1]

    # Verifica que la planta esté registrada
    if user_id not in plantas_por_usuario or nombre_planta not in plantas_por_usuario[user_id]:
        await update.message.reply_text(f"⚠️ La planta '{nombre_planta}' no está registrada.")
        return

    # Verifica que la planta tenga frecuencia de riego registrada
    if user_id not in riego_por_usuario or nombre_planta not in riego_por_usuario[user_id]:
        await update.message.reply_text(f"ℹ️ No hay frecuencia de riego registrada para '{nombre_planta}'. Usa /regar para configurarla.")
        return

    # Valida la fecha
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        await update.message.reply_text("❗ El formato de fecha debe ser YYYY-MM-DD (ejemplo: 2025-06-13).")
        return

    riego_por_usuario[user_id][nombre_planta]["ultimo_riego"] = fecha.isoformat()
    guardar_datos()
    await update.message.reply_text(
        f"✅ Fecha de último riego de '{nombre_planta}' actualizada a {fecha.isoformat()}."
    )

cambiar_riego_handler = CommandHandler("cambiarRiego", cambiar_riego)