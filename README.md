# Plantas-SC

Bot de Telegram para registrar, medir y gestionar el crecimiento y riego de las plantas de nuestro vivero.

---

## ¿Qué hace este proyecto?

Plantas-SC es un bot de Telegram que permite a los usuarios:
- Registrar plantas por nombre.
- Ver la lista de plantas registradas.
- Eliminar plantas.
- Medir la estatura de una planta y guardar el historial de medidas.
- Consultar la última estatura registrada de una planta.
- Configurar y registrar la frecuencia de riego de cada planta.
- Consultar y modificar la frecuencia y la fecha del último riego.
- Recibir recordatorios automáticos cuando toca regar una planta.

---

## Estructura del proyecto

```
Plantas-SC/
│
├── main.py                  # Punto de entrada del proyecto
├── requirements.txt         # Dependencias del proyecto
├── .gitignore               # Archivos y carpetas ignorados por git
├── README.md                # Este archivo
├── data/                    # Archivos JSON persistentes de datos
│   ├── plantas.json
│   ├── medidas.json
│   └── riego.json
└── src/
    ├── __init__.py
    ├── bot.py               # Configuración y arranque del bot
    ├── handlers/            # Handlers de comandos y conversaciones
    │   ├── __init__.py
    │   ├── start.py             # /start
    │   ├── register.py          # /registrar
    │   ├── view_plants.py       # /verplantas
    │   ├── delete.py            # /eliminar
    │   ├── measure.py           # /medir (ConversationHandler)
    │   ├── high.py              # /estatura (ConversationHandler)
    │   ├── water.py             # /regar
    │   ├── consult_watering.py  # /consultarRiego
    │   ├── change_watering.py   # /cambiarRiego
    │   ├── change_frequency.py  # /cambiarFrecuencia
    │   └── reminder.py          # Job de recordatorio de riego
    └── utils/
        ├── __init__.py
        └── storage.py       # Diccionarios globales de almacenamiento y persistencia
```

---

## Stack tecnológico

- **Python 3.10+**
- **[python-telegram-bot](https://python-telegram-bot.org/)** (v20+, con soporte para job-queue)
- **Telegram Bot API**
- Persistencia sencilla en archivos JSON (no requiere base de datos externa)

---

## Instalación y primera ejecución

1. **Clona el repositorio:**
   ```bash
   git clone <url-del-repo>
   cd Plantas-SC
   ```

2. **Crea y activa un entorno virtual:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Ejecuta el bot:**
   ```bash
   python main.py
   ```

---

## Ejecución (con entorno virtual ya creado y activado)

Si ya tienes el entorno virtual creado y activado, simplemente ejecuta:

```bash
python main.py
```

---

## Uso

En Telegram, inicia una conversación con tu bot y usa los siguientes comandos:

### 🍃 Consulta tus plantitas
- `/verplantas` — Ver tus plantas registradas.
- `/registrar <nombre>` — Registrar una nueva planta.
- `/eliminar <nombre>` — Eliminar una planta.

### 🌱 Crecimiento de plantas
- `/medir` — Inicia el flujo para registrar una medida de una planta.
- `/estatura` — Consulta la última medida registrada de una planta.

### 💧 Riego de plantas
- `/regar <nombre> <días>` — Configurar frecuencia y registrar riego de una planta.
- `/consultarRiego <nombre>` — Consultar frecuencia y último riego de una planta.
- `/cambiarRiego <nombre> <YYYY-MM-DD>` — Cambiar la fecha del último riego.
- `/cambiarFrecuencia <nombre> <días>` — Cambiar la frecuencia de riego.

### ❌ Otros
- `/cancelar` — Cancela cualquier acción en curso.
- `/start` — Muestra la bienvenida y los comandos disponibles.

---

## Notas importantes

- **Persistencia:** Los datos se almacenan en archivos JSON en el directorio `data/`. Si el bot se reinicia, los datos se conservan.
- **Modularidad:** Cada comando está implementado en un archivo handler independiente para facilitar el mantenimiento y la extensión.
