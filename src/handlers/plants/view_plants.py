from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from src.utils.storage import plantas_por_usuario

async def verplantas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    plantas = plantas_por_usuario.get(user_id, [])
    if not plantas:
        await update.message.reply_text("🌱 No tienes plantas registradas.")
        return

    mensaje = "🌿 Tus plantas registradas:\n"
    for idx, planta in enumerate(plantas, 1):
        mensaje += f"{idx}. {planta}\n"
    mensaje += f"\nTotal: {len(plantas)} plantas registradas."
    await update.message.reply_text(mensaje)

verplantas_handler = CommandHandler("verplantas", verplantas)