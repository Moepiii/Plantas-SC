from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from datetime import date
from src.utils.storage import plantas_por_usuario, riego_por_usuario, guardar_datos

async def regar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if len(context.args) < 2:
        await update.message.reply_text("❗ Usa: /regar <nombre_de_la_planta> <días>")
        return

    nombre_planta = " ".join(context.args[:-1]).strip()
    try:
        frecuencia = int(context.args[-1])
        if frecuencia <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❗ La frecuencia debe ser un número entero mayor a 0.")
        return

    # Verifica que la planta esté registrada
    if user_id not in plantas_por_usuario or nombre_planta not in plantas_por_usuario[user_id]:
        await update.message.reply_text(f"⚠️ La planta '{nombre_planta}' no está registrada.")
        return

    # Guarda la frecuencia y la fecha actual como último riego
    if user_id not in riego_por_usuario:
        riego_por_usuario[user_id] = {}
    riego_por_usuario[user_id][nombre_planta] = {
        "frecuencia": frecuencia,
        "ultimo_riego": date.today().isoformat()
    }
    guardar_datos()
    await update.message.reply_text(
        f"💧 Frecuencia de riego para '{nombre_planta}' registrada: cada {frecuencia} días.\n"
        f"Se registró que hoy fue regada."
    )

regar_handler = CommandHandler("regar", regar)