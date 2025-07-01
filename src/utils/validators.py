import re
from datetime import datetime, date

class ValidationError(Exception):
    """Excepción personalizada para errores de validación"""
    pass

class CommandValidator:
    """Clase para validar entradas de comandos"""
    
    @staticmethod
    def validate_plant_name(name: str) -> str:
        """Valida y normaliza el nombre de una planta"""
        if not name or not name.strip():
            raise ValidationError("El nombre de la planta no puede estar vacío")
        
        name = name.strip()
        if len(name) > 50:
            raise ValidationError("El nombre de la planta no puede tener más de 50 caracteres")
        
        # Corregir la línea con error de sintaxis
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s\-_]+$', name):
            raise ValidationError("El nombre solo puede contener letras, números, espacios, guiones y guiones bajos")
        
        return name
    
    @staticmethod
    def validate_delete_command_args(args: list) -> str:
        """Valida los argumentos del comando eliminar"""
        if not args:
            raise ValidationError("Debes proporcionar el nombre de la planta a eliminar")
        
        plant_name = " ".join(args).strip()
        
        if not plant_name:
            raise ValidationError("El nombre de la planta no puede estar vacío")
        
        # Usar la validación existente de nombres de plantas
        return CommandValidator.validate_plant_name(plant_name)
    
    @staticmethod
    def validate_user_has_plants(user_plants: list) -> list:
        """Valida que el usuario tenga plantas registradas"""
        if not user_plants:
            raise ValidationError("No tienes plantas registradas")
        
        # Filtrar plantas válidas
        valid_plants = []
        for plant in user_plants:
            try:
                validated_plant = CommandValidator.validate_plant_name(plant)
                valid_plants.append(validated_plant)
            except ValidationError:
                continue  # Ignorar plantas inválidas
        
        if not valid_plants:
            raise ValidationError("No tienes plantas válidas registradas")
        
        return valid_plants
    
    @staticmethod
    def validate_plant_exists_for_deletion(plant_name: str, user_plants: list) -> str:
        """Valida que una planta exista para ser eliminada"""
        if not user_plants:
            raise ValidationError("No tienes plantas registradas")
        
        plant_name_clean = plant_name.strip().lower()
        
        # Buscar coincidencia exacta (case-insensitive)
        matching_plants = []
        for plant in user_plants:
            if plant.strip().lower() == plant_name_clean:
                matching_plants.append(plant)
        
        if not matching_plants:
            # Sugerir plantas similares si no hay coincidencia exacta
            similar_plants = [p for p in user_plants if plant_name_clean in p.lower()]
            if similar_plants:
                suggestions = ", ".join(similar_plants[:3])
                raise ValidationError(
                    f"Planta '{plant_name}' no encontrada. "
                    f"¿Quisiste decir: {suggestions}?"
                )
            else:
                raise ValidationError(f"Planta '{plant_name}' no encontrada")
        
        return matching_plants[0]  # Retornar el nombre original con mayúsculas/minúsculas correctas
    
    @staticmethod
    def validate_deletion_impact(plant_name: str, user_id: int, related_data: dict = None) -> dict:
        """Valida el impacto de eliminar una planta (medidas, riegos, etc.)"""
        impact = {
            'measurements_count': 0,
            'watering_records': 0,
            'has_related_data': False,
            'warnings': []
        }
        
        if related_data:
            # Verificar medidas
            if 'measurements' in related_data:
                measurements = related_data['measurements'].get(user_id, {}).get(plant_name, [])
                impact['measurements_count'] = len(measurements)
                if measurements:
                    impact['has_related_data'] = True
                    impact['warnings'].append(f"Se perderán {len(measurements)} medidas registradas")
            
            # Verificar registros de riego
            if 'watering' in related_data:
                watering = related_data['watering'].get(user_id, {}).get(plant_name, [])
                impact['watering_records'] = len(watering)
                if watering:
                    impact['has_related_data'] = True
                    impact['warnings'].append(f"Se perderán {len(watering)} registros de riego")
        
        return impact
    
    @staticmethod
    def validate_bulk_deletion(plant_name: str, user_plants: list) -> dict:
        """Valida eliminación en lote (todas las plantas con el mismo nombre)"""
        plant_name_clean = plant_name.strip().lower()
        
        # Contar cuántas plantas tienen el mismo nombre
        matching_plants = [p for p in user_plants if p.strip().lower() == plant_name_clean]
        
        if not matching_plants:
            raise ValidationError(f"No se encontraron plantas con el nombre '{plant_name}'")
        
        return {
            'count': len(matching_plants),
            'plants': matching_plants,
            'is_bulk': len(matching_plants) > 1
        }
    
    @staticmethod
    def validate_hours(hours_str: str) -> float:
        """Valida las horas de servicio comunitario"""
        try:
            hours = float(hours_str)
            if hours <= 0:
                raise ValidationError("Las horas deben ser un número positivo")
            if hours > 24:
                raise ValidationError("No puedes registrar más de 24 horas por día")
            return hours
        except ValueError:
            raise ValidationError("Ingresa un número válido de horas (ejemplo: 2.5)")
    
    @staticmethod
    def delete_hours(hours_str: str) -> float:
        """Valida las horas a eliminar del servicio comunitario"""
        try:
            hours = float(hours_str)
            if hours <= 0:
                raise ValidationError("Las horas deben ser un número positivo")
            if hours > 24:
                raise ValidationError("No puedes eliminar más de 24 horas por día")
            return hours
        except ValueError:
            raise ValidationError("Ingresa un número válido de horas (ejemplo: 2.5)")
    
    @staticmethod
    def validate_date(date_str: str) -> str:
        """Valida formato de fecha YYYY-MM-DD"""
        try:
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if parsed_date > date.today():
                raise ValidationError("No puedes registrar datos para fechas futuras")
            return parsed_date.isoformat()
        except ValueError:
            raise ValidationError("Formato de fecha inválido. Usa YYYY-MM-DD (ejemplo: 2024-01-15)")
    
    @staticmethod
    def delete_date(date_str: str) -> str:
        """Valida formato de eliminación de fecha YYYY-MM-DD"""
        try:
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if parsed_date > date.today():
                raise ValidationError("No puedes eliminar datos para fechas futuras")
            return parsed_date.isoformat()
        except ValueError:
            raise ValidationError("Formato de fecha inválido. Usa YYYY-MM-DD (ejemplo: 2024-01-15)")
    
    @staticmethod
    def validate_measurement(measurement_str: str) -> float:
        """Valida medidas de plantas"""
        try:
            measurement = float(measurement_str)
            if measurement <= 0:
                raise ValidationError("La medida debe ser un número positivo")
            if measurement > 1000:  # 10 metros máximo
                raise ValidationError("La medida parece demasiado grande (máximo 1000 cm)")
            return measurement
        except ValueError:
            raise ValidationError("Ingresa una medida válida en centímetros (ejemplo: 25.5)")
    
    @staticmethod
    def validate_measurement_index(index_str, max_index):
        """Valida un índice de medida"""
        if not index_str or not index_str.strip():
            raise ValidationError("El índice no puede estar vacío.")
        
        try:
            index = int(index_str.strip())
        except ValueError:
            raise ValidationError("El índice debe ser un número entero.")
        
        if index < 1:
            raise ValidationError("El índice debe ser mayor que 0.")
        
        if index > max_index:
            raise ValidationError(f"El índice debe ser menor o igual a {max_index}.")
        
        return index

    @staticmethod
    def validate_plant_exists(plant_name, user_plants):
        """Valida que una planta exista en la lista del usuario"""
        if not user_plants:
            raise ValidationError("No tienes plantas registradas.")
        
        plant_name_clean = plant_name.strip().lower()
        
        for plant in user_plants:
            if plant.strip().lower() == plant_name_clean:
                return plant
        
        raise ValidationError(f"La planta '{plant_name}' no está registrada.")

    @staticmethod
    def validate_has_measurements(user_id, plant_name, measurements_data):
        """Valida que una planta tenga medidas registradas"""
        user_measurements = measurements_data.get(user_id, {})
        plant_measurements = user_measurements.get(plant_name, [])
        
        if not plant_measurements:
            raise ValidationError(f"La planta '{plant_name}' no tiene medidas registradas.")
        
        return plant_measurements
    
    @staticmethod
    def validate_frequency(frequency_str: str) -> int:
        """Valida frecuencia de riego en días"""
        try:
            frequency = int(frequency_str)
            if frequency <= 0:
                raise ValidationError("La frecuencia debe ser un número positivo")
            if frequency > 365:
                raise ValidationError("La frecuencia no puede ser mayor a 365 días")
            return frequency
        except ValueError:
            raise ValidationError("Ingresa un número válido de días (ejemplo: 7)")
    
    @staticmethod
    def validate_watering_command_args(args: list, min_args: int = 2) -> tuple:
        """Valida argumentos de comandos de riego"""
        if len(args) < min_args:
            if min_args == 2:
                raise ValidationError("Faltan argumentos. Uso correcto: <nombre_planta> <valor>")
            else:
                raise ValidationError("Faltan argumentos para el comando")
        
        # El último argumento es el valor, el resto es el nombre de la planta
        plant_name = " ".join(args[:-1]).strip()
        value = args[-1].strip()
        
        if not plant_name:
            raise ValidationError("El nombre de la planta no puede estar vacío")
        
        if not value:
            raise ValidationError("El valor no puede estar vacío")
        
        # Validar nombre de planta
        validated_plant_name = CommandValidator.validate_plant_name(plant_name)
        
        return validated_plant_name, value
    
    @staticmethod
    def validate_consult_watering_args(args: list) -> str:
        """Valida argumentos del comando consultar riego"""
        if not args:
            raise ValidationError("Debes proporcionar el nombre de la planta")
        
        plant_name = " ".join(args).strip()
        
        if not plant_name:
            raise ValidationError("El nombre de la planta no puede estar vacío")
        
        return CommandValidator.validate_plant_name(plant_name)
    
    @staticmethod
    def validate_plant_is_registered(plant_name: str, user_id: int, plantas_dict: dict) -> str:
        """Valida que una planta esté registrada para el usuario"""
        plantas = plantas_dict.get(user_id, [])
        
        if not plantas:
            raise ValidationError("No tienes plantas registradas. Usa `/registrar <nombre>` primero.")
        
        # Buscar la planta (case-insensitive)
        for planta in plantas:
            if planta and planta.lower().strip() == plant_name.lower().strip():
                return planta.strip()
        
        plantas_str = ", ".join(plantas)
        raise ValidationError(
            f"No tienes una planta llamada '{plant_name}'.\n"
            f"Tus plantas registradas: {plantas_str}"
        )
    
    @staticmethod
    def validate_watering_exists(plant_name: str, user_id: int, riego_por_usuario: dict) -> dict:
        """Valida que existan datos de riego para una planta"""
        if user_id not in riego_por_usuario or plant_name not in riego_por_usuario[user_id]:
            raise ValidationError(
                f"No hay frecuencia de riego registrada para '{plant_name}'.\n"
                "Usa /regar <nombre_planta> <días> para configurarla"
            )
        
        watering_data = riego_por_usuario[user_id][plant_name]
        
        # Validar estructura de datos
        if not isinstance(watering_data, dict):
            raise ValidationError("Datos de riego corruptos. Configura el riego nuevamente")
        
        if 'frecuencia' not in watering_data or 'ultimo_riego' not in watering_data:
            raise ValidationError("Datos de riego incompletos. Configura el riego nuevamente")
        
        return watering_data
    
    @staticmethod
    def validate_watering_date(date_str: str) -> str:
        """Valida fecha de riego en formato YYYY-MM-DD"""
        try:
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            # No permitir fechas futuras
            if parsed_date > date.today():
                raise ValidationError("No puedes registrar riegos para fechas futuras")
            
            # No permitir fechas muy antiguas (más de 2 años)
            two_years_ago = date.today().replace(year=date.today().year - 2)
            if parsed_date < two_years_ago:
                raise ValidationError("La fecha es demasiado antigua (máximo 2 años atrás)")
            
            return parsed_date.isoformat()
            
        except ValueError:
            raise ValidationError(
                "Formato de fecha inválido. Usa YYYY-MM-DD (ejemplo: 2024-01-15)"
            )
    
    @staticmethod
    def calculate_watering_status(watering_data: dict) -> dict:
        """Calcula el estado del riego de una planta"""
        try:
            frequency = watering_data['frecuencia']
            last_watering_str = watering_data['ultimo_riego']
            
            last_watering = datetime.strptime(last_watering_str, "%Y-%m-%d").date()
            today = date.today()
            
            days_since_watering = (today - last_watering).days
            days_until_next = frequency - days_since_watering
            
            # Determinar estado
            if days_until_next > 0:
                status = "ok"
                message = f"Próximo riego en {days_until_next} día(s)"
            elif days_until_next == 0:
                status = "due"
                message = "¡Toca regar hoy!"
            else:
                overdue_days = abs(days_until_next)
                status = "overdue"
                message = f"¡Riego atrasado por {overdue_days} día(s)!"
            
            return {
                'status': status,
                'message': message,
                'days_since_watering': days_since_watering,
                'days_until_next': days_until_next,
                'last_watering': last_watering,
                'frequency': frequency
            }
            
        except (ValueError, KeyError) as e:
            raise ValidationError("Error al calcular estado de riego. Datos corruptos")
    
    @staticmethod
    def validate_frequency_change_args(args: list) -> tuple:
        """Valida argumentos específicos para cambiar frecuencia"""
        if len(args) < 2:
            raise ValidationError(
                "Uso correcto: /cambiarFrecuencia <nombre_planta> <nueva_frecuencia_en_días>\n"
                "Ejemplo: /cambiarFrecuencia Rosa 5"
            )
        
        plant_name, frequency_str = CommandValidator.validate_watering_command_args(args, 2)
        frequency = CommandValidator.validate_frequency(frequency_str)
        
        return plant_name, frequency
    
    @staticmethod
    def validate_watering_setup_args(args: list) -> tuple:
        """Valida argumentos para configurar riego"""
        if len(args) < 1:
            raise ValidationError(
                "Uso correcto: `/regar <nombre_planta> [frecuencia_dias]`\n"
                "Ejemplo: `/regar Rosa 3`"
            )
        
        if len(args) == 1:
            # Si solo se proporciona el nombre, usar frecuencia por defecto
            plant_name = args[0].strip()
            frequency = 3  # Frecuencia por defecto de 3 días
        else:
            plant_name = " ".join(args[:-1]).strip()
            try:
                frequency = int(args[-1])
                if frequency <= 0:
                    raise ValidationError("La frecuencia debe ser un número positivo de días.")
                if frequency > 365:
                    raise ValidationError("La frecuencia no puede ser mayor a 365 días.")
            except ValueError:
                raise ValidationError("La frecuencia debe ser un número entero de días.")
        
        if not plant_name:
            raise ValidationError("El nombre de la planta no puede estar vacío.")
        
        validated_plant = CommandValidator.validate_plant_name(plant_name)
        return validated_plant, frequency
    
    @staticmethod
    def validate_change_watering_date_args(args: list) -> tuple:
        """Valida argumentos para cambiar fecha de riego"""
        if len(args) < 2:
            raise ValidationError(
                "Uso correcto: /cambiarRiego <nombre_planta> <YYYY-MM-DD>\n"
                "Ejemplo: /cambiarRiego Rosa 2024-01-15"
            )
        
        plant_name, date_str = CommandValidator.validate_watering_command_args(args, 2)
        validated_date = CommandValidator.validate_watering_date(date_str)
        
        return plant_name, validated_date