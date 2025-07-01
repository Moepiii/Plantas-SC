from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from src.utils.storage import plantas_por_usuario, medidas_por_usuario, riego_por_usuario, guardar_datos
from src.utils.validators import CommandValidator, ValidationError
from src.utils.decorators import handle_errors, track_usage
import logging

logger = logging.getLogger('plantas_bot')

@handle_errors
@track_usage("eliminar")
async def eliminar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Elimina una planta con validaciones completas"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "Usuario"
    
    try:
        # Validar argumentos del comando
        plant_name = CommandValidator.validate_delete_command_args(context.args)
        
        # Validar que el usuario tenga plantas
        user_plants = plantas_por_usuario.get(user_id, [])
        valid_plants = CommandValidator.validate_user_has_plants(user_plants)
        
        # Validar que la planta exista
        plant_to_delete = CommandValidator.validate_plant_exists_for_deletion(plant_name, valid_plants)
        
        # Validar eliminación en lote
        bulk_info = CommandValidator.validate_bulk_deletion(plant_name, valid_plants)
        
        # Validar impacto de la eliminación
        related_data = {
            'measurements': medidas_por_usuario,
            'watering': riego_por_usuario
        }
        impact = CommandValidator.validate_deletion_impact(plant_to_delete, user_id, related_data)
        
        # Proceder con la eliminación
        plantas_antes = len(plantas_por_usuario[user_id])
        
        # Eliminar todas las ocurrencias del nombre de planta
        plantas_por_usuario[user_id] = [p for p in plantas_por_usuario[user_id] if p.strip().lower() != plant_name.lower()]
        
        plantas_despues = len(plantas_por_usuario[user_id])
        plantas_eliminadas = plantas_antes - plantas_despues
        
        # Limpiar datos relacionados si existen
        if impact['has_related_data']:
            # Limpiar medidas
            if user_id in medidas_por_usuario and plant_to_delete in medidas_por_usuario[user_id]:
                del medidas_por_usuario[user_id][plant_to_delete]
            
            # Limpiar registros de riego
            if user_id in riego_por_usuario and plant_to_delete in riego_por_usuario[user_id]:
                del riego_por_usuario[user_id][plant_to_delete]
        
        # Guardar cambios
        guardar_datos()
        
        # Preparar mensaje de confirmación
        if bulk_info['is_bulk']:
            mensaje = f"🗑️ Se eliminaron {plantas_eliminadas} plantas llamadas '{plant_name}'"
        else:
            mensaje = f"🗑️ Planta '{plant_to_delete}' eliminada exitosamente"
        
        # Añadir información sobre datos relacionados eliminados
        if impact['has_related_data']:
            mensaje += "\n\n📊 Datos relacionados eliminados:"
            if impact['measurements_count'] > 0:
                mensaje += f"\n📏 {impact['measurements_count']} medidas"
            if impact['watering_records'] > 0:
                mensaje += f"\n💧 {impact['watering_records']} registros de riego"
        
        # Añadir estadísticas finales
        plantas_restantes = len(plantas_por_usuario[user_id])
        mensaje += f"\n\n🌱 Plantas restantes: {plantas_restantes}"
        
        if plantas_restantes == 0:
            mensaje += "\n💡 Usa /registrar <nombre> para registrar una nueva planta"
        else:
            mensaje += "\n💡 Usa /verplantas para ver tus plantas restantes"
        
        await update.message.reply_text(mensaje)
        
        # Log de la acción
        logger.info(f"Usuario {username} ({user_id}) eliminó {plantas_eliminadas} planta(s) '{plant_name}'")
        
    except ValidationError as e:
        await update.message.reply_text(f"❌ {str(e)}")
        
    except Exception as e:
        logger.error(f"Error inesperado al eliminar planta para usuario {username} ({user_id}): {e}")
        await update.message.reply_text(
            "❌ Error inesperado al eliminar la planta. Inténtalo de nuevo.\n\n"
            "Si el problema persiste, contacta al administrador."
        )

@handle_errors
async def mostrar_ayuda_eliminar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra ayuda detallada para el comando eliminar"""
    mensaje = """
🗑️ **COMANDO ELIMINAR**

**Uso:**
`/eliminar <nombre_de_la_planta>`

**Ejemplos:**
• `/eliminar Rosa` - Elimina la planta llamada "Rosa"
• `/eliminar Cactus del jardín` - Elimina la planta con nombre completo

**Importante:**
⚠️ Si tienes varias plantas con el mismo nombre, se eliminarán TODAS
⚠️ También se eliminarán las medidas y registros de riego asociados
⚠️ Esta acción NO se puede deshacer

**Comandos relacionados:**
• `/verplantas` - Ver todas tus plantas
• `/registrar <nombre>` - Registrar una nueva planta

💡 **Tip:** Usa `/verplantas` primero para ver el nombre exacto de tus plantas
"""
    
    await update.message.reply_text(mensaje)

# Handlers
eliminar_handler = CommandHandler("eliminar", eliminar)
ayuda_eliminar_handler = CommandHandler("ayuda_eliminar", mostrar_ayuda_eliminar)