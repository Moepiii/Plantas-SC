from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from datetime import date
from src.utils.storage import horas_por_usuario, guardar_datos

TOTAL_HORAS = 120

async def registrar_horas_de_hoy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("❗ Usa: /registrarHorasDeHoy <horas>")
        return
    try:
        horas = float(context.args[0])
        if horas <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❗ Ingresa una cantidad válida de horas.")
        return

    hoy = date.today().isoformat()
    horas_por_usuario.setdefault(user_id, [])
    # Suma si ya hay registro para hoy
    for registro in horas_por_usuario[user_id]:
        if registro["fecha"] == hoy:
            registro["horas"] += horas
            break
    else:
        horas_por_usuario[user_id].append({"fecha": hoy, "horas": horas})
    guardar_datos()

    total = sum(r["horas"] for r in horas_por_usuario[user_id])
    faltan = max(0, TOTAL_HORAS - total)
    if faltan == 0 or total >= TOTAL_HORAS:
        msg = f"🎉 ¡Has culminado el Servicio Comunitario!\n\nResumen:\n"
        for r in sorted(horas_por_usuario[user_id], key=lambda x: x["fecha"]):
            msg += f"{r['fecha']}: {r['horas']} horas\n"
        msg += f"\nTotal: {total} horas"
    else:
        msg = f"✅ Registradas {horas} horas para hoy ({hoy}).\nTe faltan {faltan} horas para culminar el Servicio Comunitario."
    await update.message.reply_text(msg)

registrar_horas_de_hoy_handler = CommandHandler("registrarHorasDeHoy", registrar_horas_de_hoy)