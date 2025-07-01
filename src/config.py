import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    TOTAL_HORAS_SERVICIO = int(os.getenv('TOTAL_HORAS_SERVICIO', '120'))
    DATA_DIR = os.getenv('DATA_DIR', 'data')
    
    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN no está configurado en las variables de entorno")