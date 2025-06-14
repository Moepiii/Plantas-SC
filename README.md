# Plantas-SC

Bot de Telegram para registrar, medir y gestionar el crecimiento y riego de las plantas de nuestro vivero, así como el seguimiento de horas de servicio comunitario.

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
- Registrar, consultar y eliminar horas de servicio comunitario, con resumen por fecha y notificación al completar las 120 horas.

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
│   ├── riego.json
│   └── horas.json
└── src/
    ├── __init__.py
    ├── bot.py               # Configuración y arranque del bot
    ├── handlers/            # Handlers de comandos y conversaciones
    │   ├── __init__.py
    │   ├── start.py
    │   ├── help.py              # Comando /help con ayuda por secciones
    │   ├── delete_my_data.py    # /borrarMisDatos
    │   ├── reminder.py          # Job de recordatorio de riego
    │   ├── plants/
    │   │   ├── __init__.py
    │   │   ├── register.py      # /registrar
    │   │   ├── view_plants.py   # /verplantas
    │   │   ├── delete.py        # /eliminar
    │   │   ├── measure.py       # /medir (ConversationHandler)
    │   │   └── high.py          # /estatura (ConversationHandler)
    │   ├── watering/
    │   │   ├── __init__.py
    │   │   ├── water.py             # /regar
    │   │   ├── consult_watering.py  # /consultarRiego
    │   │   ├── change_watering.py   # /cambiarRiego
    │   │   └── change_frequency.py  # /cambiarFrecuencia
    │   └── hours/
    │       ├── __init__.py
    │       ├── register_hours_today.py      # /registrarHorasDeHoy
    │       ├── register_hours_with_date.py  # /registrarHorasConFecha
    │       ├── hours_summary.py             # /horasCumplidas
    │       └── delete_hours.py              # /eliminarHoras
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

En Telegram, inicia una conversación con tu bot y usa los siguientes comandos generales:

- `/start` — Muestra las acciones generales y secciones disponibles.
- `/help` — Muestra la ayuda completa con todos los comandos.
- `/help <número>` — Muestra la ayuda específica de una sección:
  - `/help 1` — Consulta tus plantitas
  - `/help 2` — Crecimiento de plantas
  - `/help 3` — Riego de plantas
  - `/help 4` — Seguimiento de horas de Servicio Comunitario

Cada sección contiene los comandos detallados para esa funcionalidad, los cuales son los siguientes:


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

### 🕒 Seguimiento de horas de Servicio Comunitario
- `/registrarHorasDeHoy <horas>` — Registrar horas para hoy.
- `/registrarHorasConFecha <horas> <YYYY-MM-DD>` — Registrar horas en otra fecha.
- `/horasCumplidas` — Ver resumen de horas cumplidas.
- `/eliminarHoras <horas> <YYYY-MM-DD>` — Eliminar horas de una fecha.

### ❌ Otros
- `/cancelar` — Cancela cualquier acción en curso.
- `/start` — Muestra las acciones generales y secciones disponibles.
- `/help` — Muestra la ayuda completa con todos los comandos.
- `/borrarMisDatos` — Elimina todos tus datos del bot.

---

## Notas importantes

- **Persistencia:** Los datos se almacenan en archivos JSON en el directorio `data/`. Si el bot se reinicia, los datos se conservan.
- **Modularidad:** Cada comando está implementado en un archivo handler independiente para facilitar el mantenimiento y la extensión.