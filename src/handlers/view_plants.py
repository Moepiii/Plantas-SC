from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from src.utils.storage import plantas_por_usuario

async def ver_plantas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    plantas = [p.strip() for p in plantas_por_usuario.get(user_id, []) if p.strip()]
    if not plantas:
        await update.message.reply_text("🌱 No tienes plantas registradas aún.")
    else:
        lista = "\n".join(f"- {p}" for p in sorted(set(plantas)))
        await update.message.reply_text(f"🌿 Tus plantas:\n{lista}")

verplantas_handler = CommandHandler("verplantas", ver_plantas)