from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from src.utils.storage import plantas_por_usuario, medidas_por_usuario, riego_por_usuario, horas_por_usuario, guardar_datos

async def borrar_mis_datos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    plantas_por_usuario.pop(user_id, None)
    medidas_por_usuario.pop(user_id, None)
    riego_por_usuario.pop(user_id, None)
    horas_por_usuario.pop(user_id, None)
    guardar_datos()
    await update.message.reply_text("🗑️ Todos tus datos han sido eliminados del bot.")

borrar_mis_datos_handler = CommandHandler("borrarMisDatos", borrar_mis_datos)