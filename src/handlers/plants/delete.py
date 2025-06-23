from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from src.utils.storage import plantas_por_usuario, guardar_datos

async def eliminar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("❗ Usa: /eliminar <nombre_de_la_planta>")
        return

    nombre = " ".join(context.args).strip()
    plantas = plantas_por_usuario.get(user_id, [])

    if not plantas:
        await update.message.reply_text("🌱 No tienes plantas registradas.")
        return

    if nombre in plantas:
        # Elimina todas las ocurrencias
        plantas_por_usuario[user_id] = [p for p in plantas if p != nombre]
        guardar_datos()
        await update.message.reply_text(f"🗑️ Todas las plantas llamadas '{nombre}' han sido eliminadas.")
    else:
        await update.message.reply_text(f"⚠️ Planta '{nombre}' no encontrada.")

eliminar_handler = CommandHandler("eliminar", eliminar)