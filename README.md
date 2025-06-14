# Plantas-SC

Bot de Telegram para registrar, medir y gestionar el crecimiento de las plantas de nuestro vivero!

---

## ¿Qué hace este proyecto?

Plantas-SC es un bot de Telegram que permite a los usuarios:
- Registrar plantas por nombre.
- Ver la lista de plantas registradas.
- Eliminar plantas.
- Medir la estatura de una planta y guardar el historial de medidas.
- Consultar la última estatura registrada de una planta.

---

## Estructura del proyecto

```
Plantas-SC/
│
├── main.py                  # Punto de entrada del proyecto
├── requirements.txt         # Dependencias del proyecto
├── .gitignore               # Archivos y carpetas ignorados por git
├── README.md                # Este archivo
└── src/
    ├── __init__.py
    ├── bot.py               # Configuración y arranque del bot
    ├── handlers/            # Handlers de comandos y conversaciones
    │   ├── __init__.py
    │   ├── start.py         # /start
    │   ├── register.py      # /registrar
    │   ├── view_plants.py   # /verplantas
    │   ├── delete.py        # /eliminar
    │   ├── measure.py       # /medir (ConversationHandler)
    │   └── high.py          # /estatura (ConversationHandler)
    └── utils/
        ├── __init__.py
        └── storage.py       # Diccionarios globales de almacenamiento
```

---

## Stack tecnológico

- **Python 3.10+**
- **[python-telegram-bot](https://python-telegram-bot.org/)** (v20+)
- **Telegram Bot API**
- No requiere base de datos externa (almacenamiento en memoria)

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

- `/start` — Muestra la bienvenida y los comandos disponibles.
- `/registrar <nombre>` — Registra una nueva planta.
- `/verplantas` — Muestra tus plantas registradas.
- `/eliminar <nombre>` — Elimina una planta.
- `/medir` — Inicia el flujo para registrar una medida de una planta.
- `/estatura` — Consulta la última medida registrada de una planta.
- `/cancelar` — Cancela cualquier acción en curso.

---

## Notas importantes

- **Persistencia:** Los datos se almacenan en memoria (diccionarios Python). Si el bot se reinicia, se pierden los datos.
- **Modularidad:** Cada comando está implementado en un archivo handler independiente para facilitar el mantenimiento y la extensión.
- **Seguridad:** No compartas tu token de bot públicamente.

---