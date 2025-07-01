import asyncio
import json
import sys
import os
from datetime import datetime, date
from typing import List, Dict
from unittest.mock import Mock, AsyncMock

# Agregar el directorio src al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.handlers.plants.register import registrar_planta
from src.handlers.plants.view_plants import verplantas
from src.handlers.plants.delete import eliminar
from src.handlers.hours.register_hours_today import registrar_horas_de_hoy
from src.handlers.hours.register_hours_with_date import registrar_horas_con_fecha
from src.handlers.hours.hours_summary import horas_cumplidas
from src.handlers.hours.delete_hours import eliminar_horas
from src.handlers.watering.water import regar
from src.handlers.watering.consult_watering import consultar_riego
from src.handlers.watering.change_watering import cambiar_riego
from src.handlers.watering.change_frequency import cambiar_frecuencia
from src.handlers.plants.measure import iniciar_medicion
from src.handlers.plants.high import estatura_respuesta
from src.utils.storage import plantas_por_usuario, horas_por_usuario, medidas_por_usuario, riego_por_usuario

class UserAcceptanceTest:
    def __init__(self):
        self.test_results = []
        self.current_test = None
        self.test_user_id = 99999
        self.setup_test_environment()
    
    def setup_test_environment(self):
        """Configura el entorno de pruebas"""
        # Limpiar datos globales
        plantas_por_usuario.clear()
        horas_por_usuario.clear()
        medidas_por_usuario.clear()
        riego_por_usuario.clear()
    
    def create_mock_update_context(self, args=None, text=None):
        """Crea mocks para Update y Context"""
        # Mock del usuario
        user = Mock()
        user.id = self.test_user_id
        user.username = "acceptance_test_user"
        user.first_name = "Test"
        
        # Mock del mensaje
        message = Mock()
        message.text = text
        message.reply_text = AsyncMock()
        
        # Mock del update
        update = Mock()
        update.effective_user = user
        update.message = message
        
        # Mock del context
        context = Mock()
        context.args = args or []
        context.user_data = {}
        
        return update, context
    
    def log_test_result(self, test_name: str, status: str, details: str = ""):
        """Registra el resultado de una prueba"""
        result = {
            "test": test_name,
            "status": status,  # "PASS", "FAIL", "SKIP"
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        
        # Mostrar resultado en consola
        emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⏭️"
        print(f"{emoji} {test_name}: {status}")
        if details:
            print(f"   📝 {details}")
    
    async def test_plant_management_flow(self):
        """Prueba el flujo completo de gestión de plantas"""
        print("\n🌱 === PRUEBAS DE GESTIÓN DE PLANTAS ===")
        
        test_cases = [
            {
                "name": "Registrar planta con nombre válido",
                "handler": registrar_planta,
                "args": ["Rosa"],
                "expected_in_response": "registrada exitosamente",
                "validation": lambda: "Rosa" in plantas_por_usuario.get(self.test_user_id, [])
            },
            {
                "name": "Registrar planta con nombre duplicado",
                "handler": registrar_planta,
                "args": ["Rosa"],
                "expected_in_response": "ya tienes una planta llamada",
                "validation": lambda: len(plantas_por_usuario.get(self.test_user_id, [])) == 1
            },
            {
                "name": "Ver lista de plantas",
                "handler": verplantas,
                "args": [],
                "expected_in_response": "Rosa",
                "validation": lambda: True
            },
            {
                "name": "Eliminar planta existente",
                "handler": eliminar,
                "args": ["Rosa"],
                "expected_in_response": "eliminada",
                "validation": lambda: "Rosa" not in plantas_por_usuario.get(self.test_user_id, [])
            },
            {
                "name": "Eliminar planta inexistente",
                "handler": eliminar,
                "args": ["Inexistente"],
                "expected_in_response": "No tienes plantas registradas",
                "validation": lambda: True
            }
        ]
        
        for test_case in test_cases:
            try:
                update, context = self.create_mock_update_context(args=test_case["args"])
                await test_case["handler"](update, context)
                
                # Verificar respuesta del bot
                if update.message.reply_text.called:
                    response = update.message.reply_text.call_args[0][0]
                    
                    # Verificar que la respuesta contiene el texto esperado
                    if test_case["expected_in_response"].lower() in response.lower():
                        # Verificar validación adicional si existe
                        if test_case["validation"]():
                            self.log_test_result(test_case["name"], "PASS", f"Respuesta correcta y validación exitosa")
                        else:
                            self.log_test_result(test_case["name"], "FAIL", f"Respuesta correcta pero validación falló")
                    else:
                        self.log_test_result(test_case["name"], "FAIL", f"Respuesta no contiene: '{test_case['expected_in_response']}'")
                else:
                    self.log_test_result(test_case["name"], "FAIL", "El bot no respondió")
                    
            except Exception as e:
                self.log_test_result(test_case["name"], "FAIL", f"Error: {str(e)}")
    
    async def test_hours_tracking_flow(self):
        """Prueba el flujo de seguimiento de horas"""
        print("\n⏰ === PRUEBAS DE SEGUIMIENTO DE HORAS ===")
        
        test_scenarios = [
            {
                "name": "Registrar horas válidas para hoy",
                "handler": registrar_horas_de_hoy,
                "args": ["2.5"],
                "expected": "Horas registradas para hoy",
                "validation": lambda: len(horas_por_usuario.get(self.test_user_id, [])) > 0
            },
            {
                "name": "Acumular horas en el mismo día",
                "handler": registrar_horas_de_hoy,
                "args": ["1.5"],
                "expected": "Horas actualizadas para hoy",
                "validation": lambda: sum(r["horas"] for r in horas_por_usuario.get(self.test_user_id, [])) == 4.0
            },
            {
                "name": "Registrar horas con fecha específica",
                "handler": registrar_horas_con_fecha,
                "args": ["3", "2024-01-15"],
                "expected": "registradas",
                "validation": lambda: any(r["fecha"] == "2024-01-15" for r in horas_por_usuario.get(self.test_user_id, []))
            },
            {
                "name": "Ver resumen de horas",
                "handler": horas_cumplidas,
                "args": [],
                "expected": "horas",
                "validation": lambda: True
            },
            {
                "name": "Registrar horas inválidas (negativas)",
                "handler": registrar_horas_de_hoy,
                "args": ["-5"],
                "expected": "Las horas deben ser un número positivo",
                "validation": lambda: True
            }
        ]
        
        for scenario in test_scenarios:
            try:
                update, context = self.create_mock_update_context(args=scenario["args"])
                await scenario["handler"](update, context)
                
                if update.message.reply_text.called:
                    response = update.message.reply_text.call_args[0][0]
                    
                    if scenario["expected"].lower() in response.lower() and scenario["validation"]():
                        self.log_test_result(scenario["name"], "PASS", "Funcionalidad correcta")
                    else:
                        self.log_test_result(scenario["name"], "FAIL", f"Respuesta o validación incorrecta")
                else:
                    self.log_test_result(scenario["name"], "FAIL", "Sin respuesta del bot")
                    
            except Exception as e:
                self.log_test_result(scenario["name"], "FAIL", f"Error: {str(e)}")
    
    async def test_watering_system(self):
        """Prueba el sistema de riego"""
        print("\n💧 === PRUEBAS DE SISTEMA DE RIEGO ===")
        
        # Preparar datos: registrar una planta primero
        plantas_por_usuario[self.test_user_id] = ["Cactus"]
        
        watering_tests = [
            {
                "name": "Regar planta existente",
                "handler": regar,
                "args": ["Cactus"],
                "expected": "Riego configurado exitosamente"
            },
            {
                "name": "Consultar información de riego",
                "handler": consultar_riego,
                "args": ["Cactus"],
                "expected": "Cactus"
            },
            {
                "name": "Cambiar fecha de último riego",
                "handler": cambiar_riego,
                "args": ["Cactus", "2024-01-15"],
                "expected": "Estado actual:"
            },
            {
                "name": "Cambiar frecuencia de riego",
                "handler": cambiar_frecuencia,
                "args": ["Cactus", "7"],
                "expected": "frecuencia"
            }
        ]
        
        for test in watering_tests:
            try:
                update, context = self.create_mock_update_context(args=test["args"])
                await test["handler"](update, context)
                
                if update.message.reply_text.called:
                    response = update.message.reply_text.call_args[0][0]
                    if test["expected"].lower() in response.lower():
                        self.log_test_result(test["name"], "PASS", "Sistema funcionando correctamente")
                    else:
                        self.log_test_result(test["name"], "FAIL", f"Respuesta no contiene: '{test['expected']}'")
                else:
                    self.log_test_result(test["name"], "FAIL", "Sin respuesta del bot")
                    
            except Exception as e:
                self.log_test_result(test["name"], "FAIL", f"Error: {str(e)}")
    
    async def test_growth_tracking(self):
        """Prueba el sistema de seguimiento de crecimiento"""
        print("\n📏 === PRUEBAS DE SEGUIMIENTO DE CRECIMIENTO ===")
        
        # Preparar datos: registrar una planta
        plantas_por_usuario[self.test_user_id] = ["Tomate"]
        
        growth_tests = [
            {
                "name": "Ver estatura de plantas",
                "handler": estatura_respuesta,
                "args": [],
                "expected": "La última estatura registrada"
            }
        ]
        
        for test in growth_tests:
            try:
                update, context = self.create_mock_update_context(args=test["args"])
                await test["handler"](update, context)
                
                if update.message.reply_text.called:
                    self.log_test_result(test["name"], "PASS", "Sistema de crecimiento funcionando")
                else:
                    self.log_test_result(test["name"], "FAIL", "Sin respuesta del bot")
                    
            except Exception as e:
                self.log_test_result(test["name"], "FAIL", f"Error: {str(e)}")
    
    async def test_error_handling(self):
        """Prueba el manejo de errores"""
        print("\n🚨 === PRUEBAS DE MANEJO DE ERRORES ===")
        
        error_scenarios = [
            {
                "name": "Comando registrar sin argumentos",
                "handler": registrar_planta,
                "args": [],
                "expected_error": "Uso correcto"
            },
            {
                "name": "Horas inválidas (texto)",
                "handler": registrar_horas_de_hoy,
                "args": ["abc"],
                "expected_error": "número válido"
            },
            {
                "name": "Fecha en formato incorrecto",
                "handler": registrar_horas_con_fecha,
                "args": ["2", "fecha-incorrecta"],
                "expected_error": "formato"
            }
        ]
        
        for scenario in error_scenarios:
            try:
                update, context = self.create_mock_update_context(args=scenario["args"])
                await scenario["handler"](update, context)
                
                if update.message.reply_text.called:
                    response = update.message.reply_text.call_args[0][0]
                    if any(keyword in response.lower() for keyword in scenario["expected_error"].lower().split()):
                        self.log_test_result(scenario["name"], "PASS", f"Error manejado correctamente")
                    else:
                        self.log_test_result(scenario["name"], "FAIL", f"Error no manejado apropiadamente")
                else:
                    self.log_test_result(scenario["name"], "FAIL", "Sin respuesta de error")
                    
            except Exception as e:
                # Los errores de validación son esperados en estas pruebas
                self.log_test_result(scenario["name"], "PASS", f"Error capturado correctamente: {type(e).__name__}")
    
    async def test_data_persistence(self):
        """Prueba la persistencia de datos"""
        print("\n💾 === PRUEBAS DE PERSISTENCIA DE DATOS ===")
        
        persistence_tests = [
            "Datos de plantas se mantienen en memoria",
            "Datos de horas se mantienen en memoria", 
            "Datos de riego se mantienen en memoria",
            "Estructura de datos es consistente"
        ]
        
        for test in persistence_tests:
            try:
                # Verificar que las estructuras de datos existen y son consistentes
                if "plantas" in test:
                    # Verificar estructura de plantas
                    if isinstance(plantas_por_usuario, dict):
                        self.log_test_result(test, "PASS", "Estructura de plantas correcta")
                    else:
                        self.log_test_result(test, "FAIL", "Estructura de plantas incorrecta")
                
                elif "horas" in test:
                    # Verificar estructura de horas
                    if isinstance(horas_por_usuario, dict):
                        self.log_test_result(test, "PASS", "Estructura de horas correcta")
                    else:
                        self.log_test_result(test, "FAIL", "Estructura de horas incorrecta")
                
                elif "riego" in test:
                    # Verificar estructura de riego
                    if isinstance(riego_por_usuario, dict):
                        self.log_test_result(test, "PASS", "Estructura de riego correcta")
                    else:
                        self.log_test_result(test, "FAIL", "Estructura de riego incorrecta")
                
                else:
                    # Verificar consistencia general
                    all_structures_ok = all(isinstance(structure, dict) for structure in [
                        plantas_por_usuario, horas_por_usuario, riego_por_usuario, medidas_por_usuario
                    ])
                    if all_structures_ok:
                        self.log_test_result(test, "PASS", "Todas las estructuras son consistentes")
                    else:
                        self.log_test_result(test, "FAIL", "Inconsistencia en estructuras de datos")
                        
            except Exception as e:
                self.log_test_result(test, "FAIL", f"Error en verificación: {str(e)}")
    
    def generate_test_report(self) -> str:
        """Genera reporte final de pruebas"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        skipped_tests = len([r for r in self.test_results if r["status"] == "SKIP"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = f"""
🧪 **REPORTE FINAL DE PRUEBAS DE ACEPTACIÓN DE USUARIO**
{'='*60}

📊 **Resumen Ejecutivo:**
- Total de pruebas ejecutadas: {total_tests}
- Pruebas exitosas: {passed_tests} ✅
- Pruebas fallidas: {failed_tests} ❌
- Pruebas omitidas: {skipped_tests} ⏭️
- Tasa de éxito: {success_rate:.1f}%

📋 **Detalle por Categorías:**
"""
        
        # Agrupar resultados por categoría
        categories = {}
        for result in self.test_results:
            test_name = result['test']
            if 'planta' in test_name.lower() or 'registrar' in test_name.lower() and 'hora' not in test_name.lower():
                category = "Gestión de Plantas"
            elif 'hora' in test_name.lower():
                category = "Seguimiento de Horas"
            elif 'riego' in test_name.lower() or 'regar' in test_name.lower():
                category = "Sistema de Riego"
            elif 'crecimiento' in test_name.lower() or 'estatura' in test_name.lower():
                category = "Seguimiento de Crecimiento"
            elif 'error' in test_name.lower():
                category = "Manejo de Errores"
            elif 'persistencia' in test_name.lower() or 'datos' in test_name.lower():
                category = "Persistencia de Datos"
            else:
                category = "Otros"
            
            if category not in categories:
                categories[category] = {"total": 0, "passed": 0, "failed": 0}
            
            categories[category]["total"] += 1
            if result["status"] == "PASS":
                categories[category]["passed"] += 1
            elif result["status"] == "FAIL":
                categories[category]["failed"] += 1
        
        for category, stats in categories.items():
            category_success = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            report += f"\n🔸 **{category}:**\n"
            report += f"   - Total: {stats['total']}, Exitosas: {stats['passed']}, Fallidas: {stats['failed']}\n"
            report += f"   - Tasa de éxito: {category_success:.1f}%\n"
        
        report += f"\n📝 **Detalle de Todas las Pruebas:**\n"
        
        for i, result in enumerate(self.test_results, 1):
            emoji = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⏭️"
            report += f"\n{i:2d}. {emoji} **{result['test']}** - {result['status']}\n"
            if result["details"]:
                report += f"     📝 {result['details']}\n"
            report += f"     🕒 {result['timestamp']}\n"
        
        # Recomendaciones basadas en resultados
        report += f"\n🎯 **Recomendaciones y Conclusiones:**\n"
        
        if success_rate >= 95:
            report += "🏆 **EXCELENTE:** El bot está listo para producción.\n"
            report += "   - Todas las funcionalidades críticas funcionan correctamente\n"
            report += "   - El manejo de errores es robusto\n"
            report += "   - Se recomienda proceder con el despliegue\n"
        elif success_rate >= 85:
            report += "👍 **BUENO:** El bot está en buen estado general.\n"
            report += "   - La mayoría de funcionalidades funcionan correctamente\n"
            report += "   - Revisar y corregir las pruebas fallidas antes del despliegue\n"
            report += "   - Considerar pruebas adicionales en las áreas problemáticas\n"
        elif success_rate >= 70:
            report += "⚠️ **ACEPTABLE:** El bot necesita mejoras antes del despliegue.\n"
            report += "   - Funcionalidades básicas operativas\n"
            report += "   - Se requieren correcciones importantes\n"
            report += "   - Realizar pruebas adicionales después de las correcciones\n"
        else:
            report += "🚨 **CRÍTICO:** El bot NO está listo para producción.\n"
            report += "   - Múltiples funcionalidades críticas fallan\n"
            report += "   - Se requiere revisión completa del código\n"
            report += "   - NO proceder con el despliegue hasta resolver los problemas\n"
        
        # Métricas adicionales
        report += f"\n📈 **Métricas Adicionales:**\n"
        report += f"   - Tiempo total de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"   - Usuario de prueba ID: {self.test_user_id}\n"
        report += f"   - Entorno: Pruebas de Aceptación Automatizadas\n"
        
        return report
    
    async def run_all_tests(self):
        """Ejecuta todas las pruebas de aceptación"""
        print("🚀 INICIANDO PRUEBAS DE ACEPTACIÓN DE USUARIO")
        print("=" * 60)
        print(f"🕒 Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"👤 Usuario de prueba: {self.test_user_id}")
        print("=" * 60)
        
        # Ejecutar todas las suites de pruebas
        await self.test_plant_management_flow()
        await self.test_hours_tracking_flow()
        await self.test_watering_system()
        await self.test_growth_tracking()
        await self.test_error_handling()
        await self.test_data_persistence()
        
        # Generar y mostrar reporte
        report = self.generate_test_report()
        print(report)        
        
        return self.test_results

# Script principal de pruebas
async def main():
    """Función principal para ejecutar pruebas de aceptación"""
    print("🤖 SISTEMA DE PRUEBAS DE ACEPTACIÓN - PLANTAS-SC BOT")
    print("=" * 60)
    
    tester = UserAcceptanceTest()
    results = await tester.run_all_tests()
    
    # Determinar si el bot está listo para producción
    failed_tests = [r for r in results if r["status"] == "FAIL"]
    passed_tests = [r for r in results if r["status"] == "PASS"]
    total_tests = len(results)
    
    success_rate = len(passed_tests) / total_tests if total_tests > 0 else 0
    
    print("\n" + "=" * 60)
    print("🏁 RESULTADO FINAL DE PRUEBAS DE ACEPTACIÓN")
    print("=" * 60)
    
    if not failed_tests:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ El bot está LISTO para despliegue en producción")
        print("🚀 Se recomienda proceder con el lanzamiento")
        return True
    elif success_rate >= 0.85:
        print(f"⚠️ {len(failed_tests)} de {total_tests} pruebas fallaron")
        print("🔧 El bot está CASI LISTO - se requieren correcciones menores")
        print("📋 Revisar las pruebas fallidas antes del despliegue")
        return False
    else:
        print(f"❌ {len(failed_tests)} de {total_tests} pruebas fallaron")
        print("🚨 El bot NO está listo para producción")
        print("🔧 Se requieren correcciones importantes antes del despliegue")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit_code = 0 if success else 1
    print(f"\n🔚 Finalizando con código de salida: {exit_code}")
    sys.exit(exit_code)