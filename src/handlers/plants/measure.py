from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from src.utils.storage import plantas_por_usuario, medidas_por_usuario, guardar_datos
from src.utils.validators import CommandValidator, ValidationError
from src.utils.decorators import handle_errors
from datetime import datetime

# Estados de la conversación
SELECCIONAR_PLANTA, INGRESAR_MEDIDA = range(2)

@handle_errors
async def iniciar_medicion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el proceso de medición de plantas"""
    user_id = update.effective_user.id
    
    if user_id not in plantas_por_usuario or not plantas_por_usuario[user_id]:
        await update.message.reply_text(
            "❌ No tienes plantas registradas.\n"
            "Usa `/registrar <nombre>` para registrar una planta primero."
        )
        return ConversationHandler.END
    
    plantas = plantas_por_usuario[user_id]
    # Crear teclado con las plantas
    teclado = [[planta] for planta in plantas]
    teclado.append(["❌ Cancelar"])
    reply_markup = ReplyKeyboardMarkup(teclado, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        "🌱 Selecciona la planta a medir:\n\n"
        "Toca el nombre de la planta o usa `/cancelar` para cancelar.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
    return SELECCIONAR_PLANTA

@handle_errors
async def seleccionar_planta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa la selección de planta"""
    user_id = update.effective_user.id
    plantas = plantas_por_usuario[user_id]
    seleccion = update.message.text.strip()
    
    if seleccion == "❌ Cancelar":
        await cancelar_medicion(update, context)
        return ConversationHandler.END

    planta_seleccionada = None

    # Intentar por nombre exacto
    for planta in plantas:
        if planta.lower() == seleccion.lower():
            planta_seleccionada = planta
            break
    
    if not planta_seleccionada:
        await update.message.reply_text(
            "❌ Selección inválida. Por favor, selecciona una planta del teclado o usa `/cancelar` para cancelar."
        )
        return SELECCIONAR_PLANTA
    
    # Guardar la planta seleccionada en context
    context.user_data['planta_seleccionada'] = planta_seleccionada
    
    # Mostrar historial si existe
    if user_id in medidas_por_usuario and planta_seleccionada in medidas_por_usuario[user_id]:
        medidas = medidas_por_usuario[user_id][planta_seleccionada]
        if medidas:
            ultima_medida = medidas[-1]
            await update.message.reply_text(
                f"📏 Planta seleccionada: {planta_seleccionada}\n\n"
                f"📊 Última medida: {ultima_medida['altura']} cm "
                f"({ultima_medida['fecha']})\n\n"
                "Ingresa la nueva medida en centímetros (ejemplo: 25.5):",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await update.message.reply_text(
                f"📏 Planta seleccionada: {planta_seleccionada}\n\n"
                "Esta será la primera medida de esta planta.\n"
                "Ingresa la medida en centímetros (ejemplo: 25.5):",
                reply_markup=ReplyKeyboardRemove()
            )
    else:
        await update.message.reply_text(
            f"📏 Planta seleccionada: {planta_seleccionada}\n\n"
            "Esta será la primera medida de esta planta.\n"
            "Ingresa la medida en centímetros (ejemplo: 25.5):",
            reply_markup=ReplyKeyboardRemove()
        )
    
    return INGRESAR_MEDIDA

@handle_errors
async def procesar_medida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa y guarda la medida con validación"""
    user_id = update.effective_user.id
    planta = context.user_data.get('planta_seleccionada')
    medida_texto = update.message.text.strip()
    
    if medida_texto == "❌ Cancelar":
        await cancelar_medicion(update, context)
        return ConversationHandler.END

    try:
        # Validar la medida usando CommandValidator
        medida_validada = CommandValidator.validate_measurement(medida_texto)
        
        # Inicializar estructuras si no existen
        if user_id not in medidas_por_usuario:
            medidas_por_usuario[user_id] = {}
        if planta not in medidas_por_usuario[user_id]:
            medidas_por_usuario[user_id][planta] = []
        
        # Calcular crecimiento si hay medidas anteriores
        medidas_anteriores = medidas_por_usuario[user_id][planta]
        mensaje_crecimiento = ""
        
        if medidas_anteriores:
            ultima_medida = medidas_anteriores[-1]['altura']
            crecimiento = medida_validada - ultima_medida
            if crecimiento > 0:
                mensaje_crecimiento = f"📈 ¡Creció {crecimiento:.1f} cm desde la última medida!"
            elif crecimiento < 0:
                mensaje_crecimiento = f"📉 Disminuyó {abs(crecimiento):.1f} cm desde la última medida."
            else:
                mensaje_crecimiento = "📊 Mantiene la misma altura."
        
        # Guardar la nueva medida
        nueva_medida = {
            'altura': medida_validada,
            'fecha': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat()
        }
        
        medidas_por_usuario[user_id][planta].append(nueva_medida)
        guardar_datos()
        
        # Mensaje de confirmación
        mensaje = f"✅ Medida registrada exitosamente\n\n"
        mensaje += f"🌱 Planta: {planta}\n"
        mensaje += f"📏 Altura: {medida_validada} cm\n"
        mensaje += f"📅 Fecha: {nueva_medida['fecha']}\n"
        
        if mensaje_crecimiento:
            mensaje += f"\n{mensaje_crecimiento}"
        
        mensaje += f"\n\n📊 Total de medidas: {len(medidas_por_usuario[user_id][planta])}"
        
        await update.message.reply_text(mensaje)
        
        # Limpiar datos del contexto
        context.user_data.clear()
        
        return ConversationHandler.END
        
    except ValidationError as e:
        await update.message.reply_text(
            f"❌ {str(e)}\n\n"
            "Por favor, ingresa una medida válida o usa `/cancelar` para cancelar.",
            reply_markup=ReplyKeyboardMarkup([["❌ Cancelar"]], one_time_keyboard=True, resize_keyboard=True)
        )
        return INGRESAR_MEDIDA

@handle_errors
async def cancelar_medicion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela el proceso de medición"""
    context.user_data.clear()
    await update.message.reply_text("❌ Medición cancelada.")
    return ConversationHandler.END

# Handler de conversación
medir_handler = ConversationHandler(
    entry_points=[CommandHandler("medir", iniciar_medicion)],
    states={
        SELECCIONAR_PLANTA: [MessageHandler(filters.TEXT & ~filters.COMMAND, seleccionar_planta)],
        INGRESAR_MEDIDA: [MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_medida)],
    },
    fallbacks=[CommandHandler("cancelar", cancelar_medicion)],
)
