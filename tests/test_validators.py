import unittest
import sys
import os
from datetime import datetime, date

# Agregar el directorio src al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.validators import CommandValidator, ValidationError

class TestValidators(unittest.TestCase):
    
    def test_validate_plant_name_valid(self):
        """Prueba nombres de plantas válidos"""
        valid_names = ["Rosa", "Cactus-1", "Planta_del_jardín", "Árbol de mango", "Tomate Cherry"]
        for name in valid_names:
            try:
                result = CommandValidator.validate_plant_name(name)
                self.assertEqual(result, name.strip())
            except ValidationError as e:
                self.fail(f"Nombre válido '{name}' fue rechazado: {e}")
    
    def test_validate_plant_name_invalid(self):
        """Prueba nombres de plantas inválidos"""
        invalid_cases = [
            ("", "nombre vacío"),
            ("   ", "solo espacios"),
            ("a" * 51, "nombre muy largo"),
            ("Planta@#$%", "caracteres especiales inválidos")
        ]
        
        for name, description in invalid_cases:
            with self.subTest(name=name, description=description):
                with self.assertRaises(ValidationError):
                    CommandValidator.validate_plant_name(name)
    
    def test_validate_hours_valid(self):
        """Prueba horas válidas"""
        valid_cases = [
            ("1", 1.0),
            ("2.5", 2.5),
            ("8", 8.0),
            ("0.5", 0.5),
            ("12", 12.0),
            ("4.25", 4.25)
        ]
        
        for hours_str, expected in valid_cases:
            with self.subTest(hours=hours_str):
                result = CommandValidator.validate_hours(hours_str)
                self.assertEqual(result, expected)
    
    def test_validate_hours_invalid(self):
        """Prueba horas inválidas"""
        invalid_cases = [
            ("0", "cero horas"),
            ("-1", "horas negativas"),
            ("25", "más de 24 horas"),
            ("abc", "texto no numérico"),
            ("", "cadena vacía"),
            ("1.5.5", "formato decimal inválido")
        ]
        
        for hours_str, description in invalid_cases:
            with self.subTest(hours=hours_str, description=description):
                with self.assertRaises(ValidationError):
                    CommandValidator.validate_hours(hours_str)
    
    def test_validate_date_valid(self):
        """Prueba fechas válidas"""
        valid_dates = [
            "2024-01-15",
            "2023-12-31",
            "2024-02-29",  # Año bisiesto
            datetime.now().strftime('%Y-%m-%d')  # Fecha actual
        ]
        
        for date_str in valid_dates:
            with self.subTest(date=date_str):
                try:
                    result = CommandValidator.validate_date(date_str)
                    self.assertIsInstance(result, str)
                except ValidationError as e:
                    self.fail(f"Fecha válida '{date_str}' fue rechazada: {e}")
    
    def test_validate_date_invalid(self):
        """Prueba fechas inválidas"""
        invalid_dates = [
            "2024-13-01",  # Mes inválido
            "2024-02-30",  # Día inválido para febrero
            "2023-02-29",  # 29 de febrero en año no bisiesto
            "invalid-date",
            "2024/01/15",  # Formato incorrecto
            ""
        ]
        
        for date_str in invalid_dates:
            with self.subTest(date=date_str):
                with self.assertRaises(ValidationError):
                    CommandValidator.validate_date(date_str)
    
    def test_validate_measurement_valid(self):
        """Prueba medidas válidas"""
        valid_measurements = [
            ("10", 10.0),
            ("15.5", 15.5),
            ("100", 100.0),
            ("0.1", 0.1),
            ("250.75", 250.75)
        ]
        
        for measurement_str, expected in valid_measurements:
            with self.subTest(measurement=measurement_str):
                result = CommandValidator.validate_measurement(measurement_str)
                self.assertEqual(result, expected)
    
    def test_validate_measurement_invalid(self):
        """Prueba medidas inválidas"""
        invalid_measurements = [
            "0",      # Cero
            "-5",     # Negativo
            "1001",   # Muy grande
            "abc",    # No numérico
            "",       # Vacío
        ]
        
        for measurement_str in invalid_measurements:
            with self.subTest(measurement=measurement_str):
                with self.assertRaises(ValidationError):
                    CommandValidator.validate_measurement(measurement_str)
    
    def test_validate_watering_frequency_valid(self):
        """Prueba frecuencias de riego válidas"""
        valid_frequencies = [1, 2, 3, 7, 14, 30]
        
        for freq in valid_frequencies:
            with self.subTest(frequency=freq):
                result = CommandValidator.validate_frequency(str(freq))
                self.assertEqual(result, freq)
    
    def test_validate_watering_frequency_invalid(self):
        """Prueba frecuencias de riego inválidas"""
        invalid_frequencies = ["0", "-1", "366", "abc", ""]
        
        for freq_str in invalid_frequencies:
            with self.subTest(frequency=freq_str):
                with self.assertRaises(ValidationError):
                    CommandValidator.validate_frequency(freq_str)
    
    def test_validate_user_has_plants(self):
        """Prueba validación de plantas del usuario"""
        # Usuario con plantas válidas
        valid_plants = ["Rosa", "Cactus", "Tomate"]
        result = CommandValidator.validate_user_has_plants(valid_plants)
        self.assertEqual(result, valid_plants)
        
        # Usuario sin plantas
        with self.assertRaises(ValidationError):
            CommandValidator.validate_user_has_plants([])
        
        with self.assertRaises(ValidationError):
            CommandValidator.validate_user_has_plants(None)
    
    def test_validate_plant_exists_for_deletion(self):
        """Prueba validación de planta existente para eliminación"""
        user_plants = ["Rosa", "Cactus", "Tomate Cherry"]
        
        # Planta existente (case insensitive)
        result = CommandValidator.validate_plant_exists_for_deletion("rosa", user_plants)
        self.assertEqual(result, "Rosa")
        
        result = CommandValidator.validate_plant_exists_for_deletion("CACTUS", user_plants)
        self.assertEqual(result, "Cactus")
        
        # Planta no existente
        with self.assertRaises(ValidationError):
            CommandValidator.validate_plant_exists_for_deletion("Inexistente", user_plants)

if __name__ == '__main__':
    # Configurar para mostrar más detalles en los tests
    unittest.main(verbosity=2)