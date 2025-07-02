from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from datetime import date
from src.utils.storage import plantas_por_usuario, riego_por_usuario, guardar_datos
from src.utils.validators import CommandValidator, ValidationError
from src.utils.decorators import handle_errors, track_usage
import logging

logger = logging.getLogger('plantas_bot')

@handle_errors
@track_usage("regar")
async def regar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Configura el riego de una planta con validaciones completas"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "Usuario"
    
    try:
        # Validar argumentos del comando
        plant_name, frequency = CommandValidator.validate_watering_setup_args(context.args)
        
        # Validar que la planta esté registrada
        validated_plant = CommandValidator.validate_plant_is_registered(
            plant_name, user_id, plantas_por_usuario
        )
        
        # Verificar si ya existe configuración de riego
        existing_watering = None
        if (user_id in riego_por_usuario and 
            validated_plant in riego_por_usuario[user_id]):
            existing_watering = riego_por_usuario[user_id][validated_plant]
        
        # Inicializar estructura si no existe
        if user_id not in riego_por_usuario:
            riego_por_usuario[user_id] = {}
        
        # Configurar riego
        today = date.today().isoformat()
        riego_por_usuario[user_id][validated_plant] = {
            "frecuencia": frequency,
            "ultimo_riego": today
        }
        
        guardar_datos()
        
        # Calcular próximo riego
        next_watering = date.today().replace(day=date.today().day + frequency)
        
        # Preparar mensaje
        if existing_watering:
            old_frequency = existing_watering.get("frecuencia", "desconocida")
            mensaje = f"🔄 Configuración de riego actualizada\n\n"
            mensaje += f"🌱 Planta: {validated_plant}\n"
            mensaje += f"📅 Frecuencia anterior: cada {old_frequency} día(s)\n"
            mensaje += f"📅 Nueva frecuencia: cada {frequency} día(s)\n"
            mensaje += f"💧 Último riego registrado: hoy ({today})\n"
            mensaje += f"📅 Próximo riego: {next_watering.strftime('%Y-%m-%d')}"
        else:
            mensaje = f"💧 Riego configurado exitosamente\n\n"
            mensaje += f"🌱 Planta: {validated_plant}\n"
            mensaje += f"📅 Frecuencia: cada {frequency} día(s)\n"
            mensaje += f"💧 Último riego registrado: hoy ({today})\n"
            mensaje += f"📅 Próximo riego: {next_watering.strftime('%Y-%m-%d')}"
        
        await update.message.reply_text(mensaje, parse_mode='Markdown')
        
        # Log de la acción
        action = "actualizó" if existing_watering else "configuró"
        logger.info(f"Usuario {username} ({user_id}) {action} riego de '{validated_plant}' a {frequency} días")
        
    except ValidationError as e:
        await update.message.reply_text(f"❗ {str(e)}")
        
    except Exception as e:
        logger.error(f"Error en regar para usuario {user_id}: {str(e)}")
        await update.message.reply_text(
            "❌ Ocurrió un error al configurar el riego. Inténtalo de nuevo."
        )

regar_handler = CommandHandler("regar", regar)