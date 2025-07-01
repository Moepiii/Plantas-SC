from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from datetime import datetime
from src.utils.decorators import handle_errors
from src.utils.validators import CommandValidator, ValidationError
from src.utils.storage import horas_por_usuario, guardar_datos, TOTAL_HORAS

@handle_errors
async def eliminar_horas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if len(context.args) < 2:
        await update.message.reply_text("❗ Usa: /eliminarHoras <horas> <YYYY-MM-DD>")
        return
    
    try:
        
        # Validar horas
        horas = CommandValidator.delete_hours(context.args[0])
        
        # Valida que el formato de fecha ingresado sea correcto
        fecha = CommandValidator.delete_date(context.args[1])
        
        horas = float(context.args[0])
        fecha = datetime.strptime(context.args[1], "%Y-%m-%d").date().isoformat()
    except ValidationError as e:
        await update.message.reply_text(f"❗ {str(e)}")
        return

    registros = horas_por_usuario.get(user_id, [])
    for registro in registros:
        if registro["fecha"] == fecha:
            if registro["horas"] <= horas:
                registros.remove(registro)
            else:
                registro["horas"] -= horas
            guardar_datos()
            break
    else:
        await update.message.reply_text("No hay horas registradas para esa fecha.")
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

eliminar_horas_handler = CommandHandler("eliminarHoras", eliminar_horas)