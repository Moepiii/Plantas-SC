from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler
from datetime import datetime
from src.utils.validators import CommandValidator, ValidationError
from src.utils.storage import plantas_por_usuario, medidas_por_usuario, guardar_datos
import logging

logger = logging.getLogger(__name__)

# Estados de la conversación
ELEGIR_PLANTA, INGRESAR_MEDIDA = range(2)

async def estatura_respuesta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra la estatura de las plantas del usuario"""
    user_id = update.effective_user.id
    
    try:
        # Verificar que el usuario tenga plantas registradas
        plantas = plantas_por_usuario.get(user_id, [])
        if not plantas:
            await update.message.reply_text(
                "🌱 No tienes plantas registradas.\n"
                "Usa `/registrar <nombre>` para registrar una planta."
            )
            return
        
        # Verificar que haya medidas registradas
        medidas_usuario = medidas_por_usuario.get(user_id, {})
        if not medidas_usuario:
            await update.message.reply_text(
                "📏 No tienes medidas registradas para ninguna planta.\n"
                "Usa `/medir` para registrar medidas de tus plantas."
            )
            return
        
        mensaje = "📏 **Estaturas de tus plantas:**\n\n"
        plantas_con_medidas = False
        
        for planta in plantas:
            if planta and planta.strip():  # Verificar que la planta no sea None o vacía
                planta_limpia = planta.strip()
                if planta_limpia in medidas_usuario and medidas_usuario[planta_limpia]:
                    plantas_con_medidas = True
                    medidas = medidas_usuario[planta_limpia]
                    ultima_medida = medidas[-1]  # Última medida registrada
                    
                    mensaje += f"🌱 **{planta_limpia}:**\n"
                    mensaje += f"   📏 Altura actual: {ultima_medida['altura']} cm\n"
                    mensaje += f"   📅 Última medición: {ultima_medida['fecha']}\n"
                    mensaje += f"   📊 Total de medidas: {len(medidas)}\n\n"
        
        if not plantas_con_medidas:
            mensaje = "📏 **La última estatura registrada:**\n\n"
            mensaje += "No tienes medidas registradas para ninguna de tus plantas.\n"
            mensaje += "Usa `/medir` para comenzar a registrar el crecimiento de tus plantas."
        else:
            mensaje += "💡 Usa `/medir` para registrar nuevas medidas."
        
        await update.message.reply_text(mensaje, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error en estatura_respuesta para usuario {user_id}: {str(e)}")
        await update.message.reply_text(
            "❌ Ocurrió un error al consultar las estaturas. Inténtalo de nuevo."
        )

async def medir_cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela el proceso de medición"""
    context.user_data.clear()
    await update.message.reply_text("❌ Acción cancelada.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

estatura_handler = CommandHandler("estatura", estatura_respuesta)