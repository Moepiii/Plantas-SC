from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from src.utils.storage import plantas_por_usuario, guardar_datos

async def registrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if len(context.args) == 0:
        await update.message.reply_text("❗ Usa: /registrar <nombre_de_la_planta>")
        return

    nombre_planta = " ".join(context.args).strip()
    if not nombre_planta:
        await update.message.reply_text("❗ El nombre de la planta no puede estar vacío.")
        return

    if user_id not in plantas_por_usuario:
        plantas_por_usuario[user_id] = []

    if nombre_planta in plantas_por_usuario[user_id]:
        await update.message.reply_text(f"⚠️ La planta '{nombre_planta}' ya está registrada.")
    else:
        plantas_por_usuario[user_id].append(nombre_planta)
        guardar_datos()
        await update.message.reply_text(f"✅ Planta '{nombre_planta}' registrada exitosamente.")

registrar_handler = CommandHandler("registrar", registrar)