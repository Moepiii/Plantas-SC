from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from src.utils.storage import plantas_por_usuario, guardar_datos
from src.utils.validators import CommandValidator, ValidationError
from src.utils.decorators import handle_errors, track_usage

@handle_errors
@track_usage("registrar")
async def registrar_planta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Registra una nueva planta con validación"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text(
            "❌ Debes proporcionar el nombre de la planta.\n"
            "Uso: `/registrar <nombre>`\n\n"
            "Ejemplo: `/registrar Rosa del jardín`"
        )
        return
    
    nombre_planta = " ".join(context.args)
    
    try:
        # Validar el nombre usando CommandValidator
        nombre_validado = CommandValidator.validate_plant_name(nombre_planta)
        
        # Verificar si el usuario ya tiene plantas registradas
        if user_id not in plantas_por_usuario:
            plantas_por_usuario[user_id] = []
        
        # Verificar si la planta ya existe
        if nombre_validado.lower() in [p.lower() for p in plantas_por_usuario[user_id]]:
            await update.message.reply_text(
                f"⚠️ Ya tienes una planta llamada '{nombre_validado}' registrada.\n"
                "Usa `/verplantas` para ver todas tus plantas."
            )
            return
        
        # Registrar la planta
        plantas_por_usuario[user_id].append(nombre_validado)
        guardar_datos()
        
        await update.message.reply_text(
            f"🌱 ¡Planta '{nombre_validado}' registrada exitosamente!\n\n"
            f"📋 Ahora tienes {len(plantas_por_usuario[user_id])} planta(s) registrada(s).\n"
            "Usa `/verplantas` para ver todas tus plantas."
        )
        
    except ValidationError as e:
        await update.message.reply_text(f"❌ {str(e)}")
    except Exception as e:
        await update.message.reply_text(
            "❌ Error inesperado al registrar la planta. Inténtalo de nuevo."
        )

# Handler
registrar_handler = CommandHandler("registrar", registrar_planta)