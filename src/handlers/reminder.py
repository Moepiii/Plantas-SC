from datetime import date, timedelta, datetime
from src.utils.storage import riego_por_usuario, guardar_datos

async def revisar_riegos(context):
    for user_id, plantas in riego_por_usuario.items():
        for nombre_planta, datos in plantas.items():
            frecuencia = datos.get("frecuencia")
            ultimo_riego = datos.get("ultimo_riego")
            if not frecuencia or not ultimo_riego:
                continue
            try:
                fecha_ultimo = datetime.strptime(ultimo_riego, "%Y-%m-%d").date()
            except Exception:
                continue
            proximo_riego = fecha_ultimo + timedelta(days=frecuencia)
            if date.today() >= proximo_riego:
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"🌱 Hoy toca regar '{nombre_planta}'!"
                    )
                    # Actualiza la fecha de último riego para evitar mensajes repetidos
                    riego_por_usuario[user_id][nombre_planta]["ultimo_riego"] = date.today().isoformat()
                    guardar_datos()
                except Exception:
                    continue