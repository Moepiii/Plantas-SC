from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes
)
from src.utils.storage import plantas_por_usuario, medidas_por_usuario, guardar_datos
from src.utils.validators import CommandValidator, ValidationError
from src.utils.decorators import handle_errors, track_usage
import logging

logger = logging.getLogger('plantas_bot')

ELEGIR_PLANTA, ELEGIR_MEDIDA = range(2)

@handle_errors
@track_usage("eliminar_medida")
async def eliminar_medida_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el proceso de eliminación de medidas"""
    user_id = update.effective_user.id
    
    # Validar que el usuario tenga plantas registradas
    plantas = plantas_por_usuario.get(user_id, [])
    plantas_validas = []
    
    # Validar cada planta y filtrar las válidas
    for planta in plantas:
        try:
            planta_validada = CommandValidator.validate_plant_name(planta)
            if planta_validada.strip():
                plantas_validas.append(planta_validada)
        except ValidationError:
            logger.warning(f"Planta inválida encontrada para usuario {user_id}: {planta}")
            continue
    
    if not plantas_validas:
        await update.message.reply_text(
            "❌ No tienes plantas registradas válidas.\n"
            "Usa `/registrar <nombre>` para registrar una planta."
        )
        return ConversationHandler.END
    
    # Crear teclado con plantas válidas
    teclado = [[planta] for planta in plantas_validas]
    teclado.append(["❌ Cancelar"])
    
    reply_markup = ReplyKeyboardMarkup(
        teclado, 
        one_time_keyboard=True, 
        resize_keyboard=True
    )
    
    await update.message.reply_text(
        "🌿 **Eliminar medida de planta**\n\n"
        "Selecciona la planta de la que quieres eliminar una medida:\n\n"
        "💡 Usa `/cancelar` en cualquier momento para cancelar.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return ELEGIR_PLANTA

@handle_errors
async def eliminar_medida_elegir_planta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa la selección de planta y muestra sus medidas"""
    user_id = update.effective_user.id
    planta_input = update.message.text.strip()
    
    # Verificar si el usuario quiere cancelar
    if planta_input.lower() in ["❌ cancelar", "cancelar"]:
        return await eliminar_medida_cancelar(update, context)
    
    try:
        # Validar el nombre de la planta
        planta_validada = CommandValidator.validate_plant_name(planta_input)
        
        # Verificar que la planta existe en la lista del usuario
        plantas_usuario = plantas_por_usuario.get(user_id, [])
        planta_encontrada = None
        
        for planta in plantas_usuario:
            if planta.lower().strip() == planta_validada.lower().strip():
                planta_encontrada = planta
                break
        
        if not planta_encontrada:
            await update.message.reply_text(
                "⚠️ Esa planta no está en tu lista.\n"
                "Por favor, selecciona una planta del teclado mostrado."
            )
            return ELEGIR_PLANTA
        
        # Verificar que la planta tenga medidas
        medidas = medidas_por_usuario.get(user_id, {}).get(planta_encontrada, [])
        
        if not medidas:
            await update.message.reply_text(
                f"📏 La planta '{planta_encontrada}' no tiene medidas registradas.\n\n"
                "Usa `/medir` para registrar medidas primero.",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        
        # Validar que las medidas sean válidas
        medidas_validas = []
        for i, medida in enumerate(medidas):
            try:
                # Si la medida es un diccionario (formato nuevo)
                if isinstance(medida, dict):
                    altura = medida.get('altura', 0)
                    fecha = medida.get('fecha', 'Sin fecha')
                    medidas_validas.append({
                        'altura': float(altura),
                        'fecha': fecha,
                        'indice_original': i
                    })
                else:
                    # Si la medida es un número (formato antiguo)
                    altura_validada = CommandValidator.validate_measurement(str(medida))
                    medidas_validas.append({
                        'altura': altura_validada,
                        'fecha': 'Sin fecha',
                        'indice_original': i
                    })
            except (ValidationError, ValueError, TypeError) as e:
                logger.warning(f"Medida inválida encontrada para {planta_encontrada}: {medida}")
                continue
        
        if not medidas_validas:
            await update.message.reply_text(
                f"❌ La planta '{planta_encontrada}' no tiene medidas válidas para eliminar.",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        
        # Guardar información en el contexto
        context.user_data["planta_seleccionada"] = planta_encontrada
        context.user_data["medidas_validas"] = medidas_validas
        
        # Mostrar las medidas con índices
        medidas_texto = ""
        for i, medida in enumerate(medidas_validas):
            medidas_texto += f"{i+1}. {medida['altura']} cm"
            if medida['fecha'] != 'Sin fecha':
                medidas_texto += f" ({medida['fecha']})"
            medidas_texto += "\n"
        
        mensaje = f"📏 Medidas de '{planta_encontrada}':\n\n"
        mensaje += medidas_texto
        mensaje += "\nEscribe el NÚMERO de la medida que deseas eliminar.\n\n"
        mensaje += "💡 Usa /cancelar para cancelar."
        
        await update.message.reply_text(
            mensaje,
            reply_markup=ReplyKeyboardRemove()
        )
        
        return ELEGIR_MEDIDA
        
    except ValidationError as e:
        await update.message.reply_text(
            f"❌ {str(e)}\n"
            "Por favor, selecciona una planta válida del teclado."
        )
        return ELEGIR_PLANTA
    except Exception as e:
        logger.error(f"Error al procesar selección de planta: {e}")
        await update.message.reply_text(
            "❌ Error inesperado. Inténtalo de nuevo."
        )
        return ConversationHandler.END

@handle_errors
async def eliminar_medida_confirmar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirma y elimina la medida seleccionada"""
    user_id = update.effective_user.id
    planta = context.user_data.get("planta_seleccionada")
    medidas_validas = context.user_data.get("medidas_validas", [])
    
    if not planta or not medidas_validas:
        await update.message.reply_text(
            "❌ Error: información de sesión perdida. Inicia el proceso nuevamente.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    try:
        # Validar el índice ingresado
        indice_input = update.message.text.strip()
        
        # Validar que sea un número
        try:
            indice = int(indice_input)
        except ValueError:
            await update.message.reply_text(
                f"❗ Por favor, ingresa un numero valido de la lista.\n\n"
                f"Opciones validas: 1 a {len(medidas_validas)}"
            )
            return ELEGIR_MEDIDA
        
        # Validar que el índice esté en el rango válido
        if indice < 1 or indice > len(medidas_validas):
            await update.message.reply_text(
                f"❗ Numero fuera de rango. Por favor, ingresa un numero entre 1 y {len(medidas_validas)}."
            )
            return ELEGIR_MEDIDA
        
        # Obtener la medida a eliminar
        medida_seleccionada = medidas_validas[indice - 1]
        indice_original = medida_seleccionada['indice_original']
        
        # Eliminar la medida del almacenamiento
        medidas_originales = medidas_por_usuario.get(user_id, {}).get(planta, [])
        
        if indice_original >= len(medidas_originales):
            await update.message.reply_text(
                "❌ Error: la medida ya no existe. El proceso se cancelará.",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        
        medida_eliminada = medidas_originales.pop(indice_original)
        
        # Guardar los cambios
        guardar_datos()
        
        # Limpiar datos de contexto
        context.user_data.clear()
        
        # Mensaje de confirmación
        altura_eliminada = medida_seleccionada['altura']
        fecha_info = f" del {medida_seleccionada['fecha']}" if medida_seleccionada['fecha'] != 'Sin fecha' else ""
        
        mensaje = f"✅ Medida eliminada exitosamente\n\n"
        mensaje += f"🌱 Planta: {planta}\n"
        mensaje += f"📏 Medida eliminada: {altura_eliminada} cm{fecha_info}\n\n"
        mensaje += f"📊 Medidas restantes: {len(medidas_originales)}"
        
        await update.message.reply_text(
            mensaje,
            reply_markup=ReplyKeyboardRemove()
        )
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error al eliminar medida: {e}")
        await update.message.reply_text(
            "❌ Error inesperado al eliminar la medida. Inténtalo de nuevo.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

@handle_errors
async def eliminar_medida_cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela el proceso de eliminación de medidas"""
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Eliminacion de medida cancelada.\n\n"
        "Puedes usar /eliminar_medida cuando quieras intentarlo de nuevo.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# Handler del ConversationHandler
eliminar_medida_handler = ConversationHandler(
    entry_points=[CommandHandler("eliminar_medida", eliminar_medida_inicio)],
    states={
        ELEGIR_PLANTA: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, 
                eliminar_medida_elegir_planta
            )
        ],
        ELEGIR_MEDIDA: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, 
                eliminar_medida_confirmar
            )
        ],
    },
    fallbacks=[
        CommandHandler("cancelar", eliminar_medida_cancelar),
        MessageHandler(filters.COMMAND, eliminar_medida_cancelar)
    ],
)
