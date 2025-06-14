from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from src.utils.storage import horas_por_usuario

TOTAL_HORAS = 120

async def horas_cumplidas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    registros = horas_por_usuario.get(user_id, [])
    if not registros:
        await update.message.reply_text("Aún no has registrado horas.")
        return

    total = sum(r["horas"] for r in registros)
    faltan = max(0, TOTAL_HORAS - total)
    resumen = "🕒 Horas cumplidas:\n"
    for r in sorted(registros, key=lambda x: x["fecha"]):
        resumen += f"{r['fecha']}: {r['horas']} horas\n"
    resumen += f"\nTotal: {total} horas\n"
    if faltan == 0 or total >= TOTAL_HORAS:
        resumen += "🎉 ¡Has culminado el Servicio Comunitario!"
    else:
        resumen += f"Te faltan {faltan} horas para culminar el Servicio Comunitario."
    await update.message.reply_text(resumen)

horas_cumplidas_handler = CommandHandler("horasCumplidas", horas_cumplidas)