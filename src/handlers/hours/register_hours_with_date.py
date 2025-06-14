from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from datetime import datetime
from src.utils.storage import horas_por_usuario, guardar_datos

TOTAL_HORAS = 120

async def registrar_horas_con_fecha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if len(context.args) < 2:
        await update.message.reply_text("❗ Usa: /registrarHorasConFecha <horas> <YYYY-MM-DD>")
        return
    try:
        horas = float(context.args[0])
        if horas <= 0:
            raise ValueError
        fecha = datetime.strptime(context.args[1], "%Y-%m-%d").date().isoformat()
    except ValueError:
        await update.message.reply_text("❗ Ingresa una cantidad válida de horas y una fecha válida (YYYY-MM-DD).")
        return

    horas_por_usuario.setdefault(user_id, [])
    for registro in horas_por_usuario[user_id]:
        if registro["fecha"] == fecha:
            registro["horas"] += horas
            break
    else:
        horas_por_usuario[user_id].append({"fecha": fecha, "horas": horas})
    guardar_datos()

    total = sum(r["horas"] for r in horas_por_usuario[user_id])
    faltan = max(0, TOTAL_HORAS - total)
    if faltan == 0 or total >= TOTAL_HORAS:
        msg = f"🎉 ¡Has culminado el Servicio Comunitario!\n\nResumen:\n"
        for r in sorted(horas_por_usuario[user_id], key=lambda x: x["fecha"]):
            msg += f"{r['fecha']}: {r['horas']} horas\n"
        msg += f"\nTotal: {total} horas"
    else:
        msg = f"✅ Registradas {horas} horas para {fecha}.\nTe faltan {faltan} horas para culminar el Servicio Comunitario."
    await update.message.reply_text(msg)

registrar_horas_con_fecha_handler = CommandHandler("registrarHorasConFecha", registrar_horas_con_fecha)