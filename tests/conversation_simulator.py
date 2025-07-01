import asyncio
import sys
import os
from unittest.mock import Mock, AsyncMock
from telegram import Update, Message, User, Chat
from telegram.ext import ContextTypes
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.handlers.plants.register import registrar_planta
from src.handlers.plants.view_plants import verplantas
from src.handlers.plants.delete import eliminar
from src.handlers.hours.register_hours_today import registrar_horas_de_hoy
from src.handlers.hours.register_hours_with_date import registrar_horas_con_fecha
from src.handlers.hours.hours_summary import horas_cumplidas
from src.handlers.watering.water import regar
from src.handlers.watering.consult_watering import consultar_riego
from src.utils.storage import plantas_por_usuario, horas_por_usuario, medidas_por_usuario, riego_por_usuario

class ConversationSimulator:
    def __init__(self):
        self.user_id = 12345
        self.chat_id = 12345
        self.username = "test_user"
        self.conversation_log = []
    
    def create_mock_update(self, text: str, command_args: list = None):
        """Crea un mock de Update para simular mensajes"""
        user = Mock(spec=User)
        user.id = self.user_id
        user.username = self.username
        user.first_name = "Test"
        user.last_name = "User"
        
        chat = Mock(spec=Chat)
        chat.id = self.chat_id
        chat.type = "private"
        
        message = Mock(spec=Message)
        message.text = text
        message.reply_text = AsyncMock()
        message.message_id = len(self.conversation_log) + 1
        message.date = datetime.now()
        
        update = Mock(spec=Update)
        update.effective_user = user
        update.effective_chat = chat
        update.message = message
        update.update_id = len(self.conversation_log) + 1
        
        return update
    
    def create_mock_context(self, args: list = None):
        """Crea un mock de Context para simular argumentos de comandos"""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.args = args or []
        context.user_data = {}
        context.chat_data = {}
        context.bot_data = {}
        return context
    
    def log_interaction(self, user_input: str, bot_response: str, status: str = "SUCCESS"):
        """Registra una interacción en el log de conversación"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "bot_response": bot_response[:200] + "..." if len(bot_response) > 200 else bot_response,
            "status": status
        }
        self.conversation_log.append(interaction)
    
    async def simulate_conversation(self, scenarios):
        """Simula una conversación completa con múltiples comandos"""
        print("🤖 Iniciando simulación de conversación...\n")
        print("=" * 60)
        
        success_count = 0
        total_count = len(scenarios)
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n--- Escenario {i}/{total_count}: {scenario['description']} ---")
            
            update = self.create_mock_update(scenario['input'])
            context = self.create_mock_context(scenario.get('args', []))
            
            try:
                # Ejecutar el handler correspondiente
                await scenario['handler'](update, context)
                
                # Verificar la respuesta
                if update.message.reply_text.called:
                    response = update.message.reply_text.call_args[0][0]
                    print(f"👤 Usuario: {scenario['input']}")
                    print(f"🤖 Bot: {response[:100]}{'...' if len(response) > 100 else ''}")
                    
                    # Verificar si la respuesta contiene el texto esperado
                    expected = scenario.get('expected', '')
                    if expected and expected.lower() in response.lower():
                        print(f"✅ Escenario completado exitosamente")
                        self.log_interaction(scenario['input'], response, "SUCCESS")
                        success_count += 1
                    elif expected:
                        print(f"⚠️ Respuesta no contiene texto esperado: '{expected}'")
                        self.log_interaction(scenario['input'], response, "PARTIAL")
                        success_count += 0.5
                    else:
                        print(f"✅ Escenario completado")
                        self.log_interaction(scenario['input'], response, "SUCCESS")
                        success_count += 1
                else:
                    print(f"❌ El bot no respondió")
                    self.log_interaction(scenario['input'], "No response", "FAILED")
                    
            except Exception as e:
                print(f"❌ Error en escenario: {str(e)}")
                self.log_interaction(scenario['input'], f"Error: {str(e)}", "ERROR")
        
        # Mostrar resumen
        print("\n" + "=" * 60)
        print(f"📊 RESUMEN DE SIMULACIÓN")
        print(f"Total de escenarios: {total_count}")
        print(f"Exitosos: {int(success_count)}")
        print(f"Tasa de éxito: {(success_count/total_count)*100:.1f}%")
        
        return success_count / total_count
    
    def generate_conversation_report(self):
        """Genera un reporte detallado de la conversación simulada"""
        report = f"""
🤖 **REPORTE DE SIMULACIÓN DE CONVERSACIÓN**
{'='*50}

📅 **Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👤 **Usuario simulado:** {self.username} (ID: {self.user_id})
💬 **Total de interacciones:** {len(self.conversation_log)}

📋 **Detalle de interacciones:**
"""
        
        for i, interaction in enumerate(self.conversation_log, 1):
            status_emoji = {
                "SUCCESS": "✅",
                "PARTIAL": "⚠️", 
                "FAILED": "❌",
                "ERROR": "🚨"
            }.get(interaction["status"], "❓")
            
            report += f"""
{i}. {status_emoji} **{interaction['status']}**
   👤 Usuario: {interaction['user_input']}
   🤖 Bot: {interaction['bot_response']}
   🕒 Tiempo: {interaction['timestamp']}
"""
        
        return report

# Escenarios de prueba predefinidos
async def run_plant_management_scenarios():
    """Ejecuta escenarios de gestión de plantas"""
    simulator = ConversationSimulator()
    
    scenarios = [
        {
            'description': 'Registrar planta nueva',
            'input': '/registrar Rosa',
            'args': ['Rosa'],
            'handler': registrar_planta,
            'expected': 'registrada exitosamente'
        },
        {
            'description': 'Registrar planta duplicada',
            'input': '/registrar Rosa',
            'args': ['Rosa'],
            'handler': registrar_planta,
            'expected': 'ya tienes una planta llamada'
        },
        {
            'description': 'Ver lista de plantas',
            'input': '/verplantas',
            'args': [],
            'handler': verplantas,
            'expected': 'Rosa'
        },
        {
            'description': 'Eliminar planta existente',
            'input': '/eliminar Rosa',
            'args': ['Rosa'],
            'handler': eliminar,
            'expected': 'eliminada'
        },
        {
            'description': 'Eliminar planta inexistente',
            'input': '/eliminar Inexistente',
            'args': ['Inexistente'],
            'handler': eliminar,
            'expected': 'No tienes plantas registradas'
        }
    ]
    
    return await simulator.simulate_conversation(scenarios)

async def run_hours_tracking_scenarios():
    """Ejecuta escenarios de seguimiento de horas"""
    simulator = ConversationSimulator()
    
    scenarios = [
        {
            'description': 'Registrar horas válidas para hoy',
            'input': '/registrarHorasDeHoy 2.5',
            'args': ['2.5'],
            'handler': registrar_horas_de_hoy,
            'expected': 'Horas registradas para hoy'
        },
        {
            'description': 'Registrar horas con fecha específica',
            'input': '/registrarHorasConFecha 3 2024-01-15',
            'args': ['3', '2024-01-15'],
            'handler': registrar_horas_con_fecha,
            'expected': 'registradas'
        },
        {
            'description': 'Ver resumen de horas',
            'input': '/horasCumplidas',
            'args': [],
            'handler': horas_cumplidas,
            'expected': 'horas'
        },
        {
            'description': 'Registrar horas inválidas',
            'input': '/registrarHorasDeHoy -5',
            'args': ['-5'],
            'handler': registrar_horas_de_hoy,
            'expected': 'Las horas deben ser un número positivo'
        }
    ]
    
    return await simulator.simulate_conversation(scenarios)

async def run_watering_scenarios():
    """Ejecuta escenarios del sistema de riego"""
    simulator = ConversationSimulator()
    
    # Primero registrar una planta para las pruebas de riego
    plantas_por_usuario[simulator.user_id] = ["Cactus"]
    
    scenarios = [
        {
            'description': 'Regar planta existente',
            'input': '/regar Cactus',
            'args': ['Cactus'],
            'handler': regar,
            'expected': 'Riego configurado exitosamente'
        },
        {
            'description': 'Consultar información de riego',
            'input': '/consultarRiego Cactus',
            'args': ['Cactus'],
            'handler': consultar_riego,
            'expected': 'Cactus'
        }
    ]
    
    return await simulator.simulate_conversation(scenarios)

async def run_comprehensive_test():
    """Ejecuta una prueba completa de todos los escenarios"""
    print("🚀 INICIANDO SIMULACIÓN COMPLETA DE CONVERSACIÓN")
    print("=" * 60)
    
    # Limpiar datos antes de empezar
    plantas_por_usuario.clear()
    horas_por_usuario.clear()
    medidas_por_usuario.clear()
    riego_por_usuario.clear()
    
    results = []
    
    print("\n🌱 === PRUEBAS DE GESTIÓN DE PLANTAS ===")
    plant_score = await run_plant_management_scenarios()
    results.append(("Gestión de Plantas", plant_score))
    
    print("\n⏰ === PRUEBAS DE SEGUIMIENTO DE HORAS ===")
    hours_score = await run_hours_tracking_scenarios()
    results.append(("Seguimiento de Horas", hours_score))
    
    print("\n💧 === PRUEBAS DE SISTEMA DE RIEGO ===")
    watering_score = await run_watering_scenarios()
    results.append(("Sistema de Riego", watering_score))
    
    # Calcular puntuación general
    overall_score = sum(score for _, score in results) / len(results)
    
    if overall_score >= 0.9:
        print("\n🏆 ¡EXCELENTE! El bot está funcionando perfectamente.")
    elif overall_score >= 0.7:
        print("\n👍 BUENO. El bot funciona bien con algunas mejoras menores.")
    else:
        print("\n⚠️ NECESITA MEJORAS. Revisar funcionalidades fallidas.")
    
    return overall_score

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())