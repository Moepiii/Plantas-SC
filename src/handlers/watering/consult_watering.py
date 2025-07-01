from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from src.utils.storage import plantas_por_usuario, riego_por_usuario
from src.utils.validators import CommandValidator, ValidationError
from src.utils.decorators import handle_errors, track_usage
import logging

logger = logging.getLogger('plantas_bot')

@handle_errors
@track_usage("consultarRiego")
async def consultar_riego(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Consulta el estado de riego de una planta con validaciones completas"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "Usuario"
    
    try:
        # Validar argumentos del comando
        plant_name = CommandValidator.validate_consult_watering_args(context.args)
        
        # Validar que la planta esté registrada
        validated_plant = CommandValidator.validate_plant_is_registered(
            plant_name, user_id, plantas_por_usuario
        )
        
        # Validar que existan datos de riego
        watering_data = CommandValidator.validate_watering_exists(
            validated_plant, user_id, riego_por_usuario
        )
        
        # Calcular estado de riego
        status_info = CommandValidator.calculate_watering_status(watering_data)
        
        # Preparar mensaje detallado
        mensaje = f"💧 **Estado de riego de '{validated_plant}'**\n\n"
        
        # Información básica
        mensaje += f"📅 **Frecuencia:** cada {status_info['frequency']} día(s)\n"
        mensaje += f"💧 **Último riego:** {status_info['last_watering']}\n"
        mensaje += f"📊 **Días desde último riego:** {status_info['days_since_watering']}\n"
        
        # Estado actual con emoji apropiado
        if status_info['status'] == 'ok':
            mensaje += f"✅ **Estado:** {status_info['message']}\n"
        elif status_info['status'] == 'due':
            mensaje += f"⏰ **Estado:** {status_info['message']}\n"
        else:  # overdue
            mensaje += f"🚨 **Estado:** {status_info['message']}\n"
        
        # Información adicional según el estado
        if status_info['status'] == 'overdue':
            mensaje += f"\n💡 **Recomendación:** Riega la planta lo antes posible"
            mensaje += f"\n🔧 **Comandos útiles:**"
            mensaje += f"\n• `/cambiarRiego {validated_plant} YYYY-MM-DD` - Actualizar fecha de último riego"
            mensaje += f"\n• `/cambiarFrecuencia {validated_plant} <días>` - Cambiar frecuencia"
        elif status_info['status'] == 'due':
            mensaje += f"\n💡 **Recomendación:** ¡Es el momento perfecto para regar!"
        else:
            mensaje += f"\n💡 **Todo está bien:** La planta no necesita riego aún"
        
        # Historial básico si hay datos
        mensaje += f"\n\n📈 **Próximos riegos:**"
        from datetime import date, timedelta
        next_date = status_info['last_watering'] + timedelta(days=status_info['frequency'])
        for i in range(3):
            future_date = next_date + timedelta(days=i * status_info['frequency'])
            mensaje += f"\n• {future_date.strftime('%Y-%m-%d')}"
        
        await update.message.reply_text(mensaje)
        
        # Log de la consulta
        logger.info(f"Usuario {username} ({user_id}) consultó riego de '{validated_plant}' - Estado: {status_info['status']}")
        
    except ValidationError as e:
        await update.message.reply_text(f"❌ {str(e)}")
        
    except Exception as e:
        logger.error(f"Error al consultar riego para usuario {username} ({user_id}): {e}")
        await update.message.reply_text(
            "❌ Error inesperado al consultar el riego. Inténtalo de nuevo."
        )

consultar_riego_handler = CommandHandler("consultarRiego", consultar_riego)