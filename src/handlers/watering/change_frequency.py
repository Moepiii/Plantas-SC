from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from src.utils.storage import plantas_por_usuario, riego_por_usuario, guardar_datos
from src.utils.validators import CommandValidator, ValidationError
from src.utils.decorators import handle_errors, track_usage
import logging

logger = logging.getLogger('plantas_bot')

@handle_errors
@track_usage("cambiarFrecuencia")
async def cambiar_frecuencia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cambia la frecuencia de riego de una planta con validaciones completas"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "Usuario"
    
    try:
        # Validar argumentos del comando
        plant_name, new_frequency = CommandValidator.validate_frequency_change_args(context.args)
        
        # Validar que la planta esté registrada
        validated_plant = CommandValidator.validate_plant_is_registered(
            plant_name, user_id, plantas_por_usuario
        )
        
        # Validar que la planta tenga configuración de riego
        watering_data = CommandValidator.validate_watering_exists(
            validated_plant, user_id, riego_por_usuario
        )
        
        # Obtener frecuencia anterior para comparación
        old_frequency = watering_data["frecuencia"]
        
        # Actualizar frecuencia
        riego_por_usuario[user_id][validated_plant]["frecuencia"] = new_frequency
        guardar_datos()
        
        # Calcular nuevo estado de riego
        updated_data = riego_por_usuario[user_id][validated_plant]
        status_info = CommandValidator.calculate_watering_status(updated_data)
        
        # Preparar mensaje de confirmación
        mensaje = f"✅ **Frecuencia de riego actualizada**\n\n"
        mensaje += f"🌱 **Planta:** {validated_plant}\n"
        mensaje += f"📅 **Frecuencia anterior:** cada {old_frequency} día(s)\n"
        mensaje += f"📅 **Nueva frecuencia:** cada {new_frequency} día(s)\n\n"
        mensaje += f"📊 **Estado actual:** {status_info['message']}\n"
        mensaje += f"💧 **Último riego:** {status_info['last_watering']}"
        
        # Añadir recomendación si es necesario
        if status_info['status'] == 'overdue':
            mensaje += f"\n\n💡 **Recomendación:** Considera regar la planta pronto"
        elif status_info['status'] == 'due':
            mensaje += f"\n\n💡 **Recomendación:** ¡Es hora de regar!"
        
        await update.message.reply_text(mensaje)
        
        # Log de la acción
        logger.info(f"Usuario {username} ({user_id}) cambió frecuencia de '{validated_plant}' de {old_frequency} a {new_frequency} días")
        
    except ValidationError as e:
        await update.message.reply_text(f"❌ {str(e)}")
        
    except Exception as e:
        logger.error(f"Error al cambiar frecuencia para usuario {username} ({user_id}): {e}")
        await update.message.reply_text(
            "❌ Error inesperado al cambiar la frecuencia. Inténtalo de nuevo."
        )

cambiar_frecuencia_handler = CommandHandler("cambiarFrecuencia", cambiar_frecuencia)