from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from datetime import date, datetime
from src.utils.decorators import handle_errors
from src.utils.validators import CommandValidator, ValidationError
from src.utils.storage import horas_por_usuario, guardar_datos, TOTAL_HORAS
import logging

logger = logging.getLogger('plantas_bot')

@handle_errors
async def registrar_horas_de_hoy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "Usuario"
    
    try:
        # Validar horas
        horas = CommandValidator.validate_hours(context.args[0])
        
        # Verificar si ya completó las horas
        horas_por_usuario.setdefault(user_id, [])
        total_actual = sum(r["horas"] for r in horas_por_usuario[user_id])
        
        if total_actual >= TOTAL_HORAS:
            await update.message.reply_text(
                "🎉 ¡Ya has completado todas las horas de servicio comunitario!\n"
                f"Total acumulado: {total_actual} horas"
            )
            return
        
        # Registrar horas
        hoy = date.today().isoformat()
        
        # Buscar si ya hay registro para hoy
        registro_existente = None
        for registro in horas_por_usuario[user_id]:
            if registro["fecha"] == hoy:
                registro_existente = registro
                break
        
        if registro_existente:
            horas_anteriores = registro_existente["horas"]
            registro_existente["horas"] += horas
            await update.message.reply_text(
                f"✅ **Horas actualizadas para hoy**\n\n"
                f" **Fecha:** {hoy}\n"
                f"⏰ **Horas anteriores:** {horas_anteriores}\n"
                f"➕ **Horas agregadas:** {horas}\n"
                f" **Total del día:** {registro_existente['horas']}\n\n"
                f"📊 **Progreso total:** {total_actual + horas}/{TOTAL_HORAS} horas\n"
                f"🎯 **Restantes:** {max(0, TOTAL_HORAS - (total_actual + horas))} horas",
                parse_mode='Markdown'
            )
        else:
            # Crear nuevo registro
            nuevo_registro = {
                "fecha": hoy,
                "horas": horas,
                "timestamp": datetime.now().isoformat()
            }
            horas_por_usuario[user_id].append(nuevo_registro)
            
            await update.message.reply_text(
                f"✅ **Horas registradas para hoy**\n\n"
                f"📅 **Fecha:** {hoy}\n"
                f"⏰ **Horas:** {horas}\n\n"
                f"📊 **Progreso total:** {total_actual + horas}/{TOTAL_HORAS} horas\n"
                f"🎯 **Restantes:** {max(0, TOTAL_HORAS - (total_actual + horas))} horas",
                parse_mode='Markdown'
            )
        
        # Guardar datos
        guardar_datos()
        
        # Log de la acción
        logger.info(f"Usuario {username} ({user_id}) registró {horas} horas para {hoy}")
        
    except ValidationError as e:
        await update.message.reply_text(f"❗ {str(e)}")
        return

# Handler para el comando
register_hours_today_handler = CommandHandler("registrarHorasDeHoy", registrar_horas_de_hoy)