from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from datetime import datetime, date
from src.utils.validators import CommandValidator, ValidationError
from src.utils.storage import riego_por_usuario, plantas_por_usuario, guardar_datos
import logging

logger = logging.getLogger(__name__)

async def cambiar_riego(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cambia la fecha del último riego de una planta"""
    user_id = update.effective_user.id
    
    try:
        # Validar argumentos
        if len(context.args) < 2:
            await update.message.reply_text(
                "❗ Uso correcto: `/cambiar_riego <nombre_planta> <fecha>`\n"
                "Ejemplo: `/cambiar_riego Rosa 2024-01-15`"
            )
            return
        
        plant_name = " ".join(context.args[:-1]).strip()
        date_str = context.args[-1]
        
        # Validar nombre de planta
        validated_plant = CommandValidator.validate_plant_name(plant_name)
        
        # Validar que la planta esté registrada
        validated_plant = CommandValidator.validate_plant_is_registered(
            validated_plant, user_id, plantas_por_usuario
        )
        
        # Validar fecha
        validated_date = CommandValidator.validate_date(date_str)
        
        # Verificar que existe configuración de riego
        if (user_id not in riego_por_usuario or 
            validated_plant not in riego_por_usuario[user_id]):
            await update.message.reply_text(
                f"❌ No hay configuración de riego para '{validated_plant}'.\n"
                f"Usa `/regar {validated_plant} <frecuencia>` para configurar el riego primero."
            )
            return
        
        # Actualizar fecha de último riego
        old_date = riego_por_usuario[user_id][validated_plant]["ultimo_riego"]
        riego_por_usuario[user_id][validated_plant]["ultimo_riego"] = validated_date
        
        guardar_datos()
        
        # Calcular próximo riego
        frequency = riego_por_usuario[user_id][validated_plant]["frecuencia"]
        next_date = datetime.strptime(validated_date, "%Y-%m-%d").date()
        next_watering = next_date.replace(day=next_date.day + frequency)
        
        mensaje = f"✅ Fecha de riego actualizada\n\n"
        mensaje += f"🌱 Planta: {validated_plant}\n"
        mensaje += f"📅 Fecha anterior: {old_date}\n"
        mensaje += f"📅 Nueva fecha: {validated_date}\n"
        mensaje += f"🔄 Frecuencia: cada {frequency} día(s)\n"
        mensaje += f"📅 Próximo riego: {next_watering.strftime('%Y-%m-%d')}\n\n"
        mensaje += f"Estado actual: Configuración actualizada correctamente"

        await update.message.reply_text(mensaje, parse_mode='Markdown')
        
    except ValidationError as e:
        await update.message.reply_text(f"❗ {str(e)}")
    except Exception as e:
        logger.error(f"Error en cambiar_riego para usuario {user_id}: {str(e)}")
        await update.message.reply_text(
            "❌ Ocurrió un error al cambiar la fecha de riego. Inténtalo de nuevo."
        )

cambiar_riego_handler = CommandHandler("cambiarRiego", cambiar_riego)