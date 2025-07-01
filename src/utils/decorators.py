import functools
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger('plantas_bot')

def handle_errors(func):
    """Decorador para manejo de errores en handlers"""
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            user_id = update.effective_user.id if update.effective_user else "Unknown"
            username = update.effective_user.username if update.effective_user else "Unknown"
            
            logger.error(f"Error en {func.__name__} para usuario {username} ({user_id}): {str(e)}")

    return wrapper

def track_usage(command_name):
    """Decorador para rastrear uso de comandos"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = update.effective_user.id if update.effective_user else "Unknown"
            
            try:
                # Registrar uso del comando
                from src.utils.metrics import bot_metrics
                bot_metrics.record_command_usage(user_id, command_name)
                
                # Ejecutar función original
                result = await func(update, context, *args, **kwargs)
                
                logger.info(f"Comando {command_name} ejecutado exitosamente por usuario {user_id}")
                return result
                
            except Exception as e:
                logger.error(f"Error en {command_name} para usuario {user_id}: {str(e)}")
                raise  # Re-lanzar para que handle_errors lo maneje
                
        return wrapper
    return decorator