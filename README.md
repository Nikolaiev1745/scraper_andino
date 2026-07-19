# 🔍 Scraper Andino — Guía Completa para No Programadores

> **¿Qué hace esta herramienta?**
> 
> Te avisa automáticamente cuando aparecen noticias sobre minería en Argentina. No tenés que estar buscando en Google todos los días. El programa lo hace por vos y te arma una planilla de Excel (en Google Sheets) con todas las noticias ordenadas por relevancia.

---

## 📋 Índice

1. [¿Para qué sirve?](#para-qué-sirve)
2. [¿Qué necesito antes de empezar?](#qué-necesito-antes-de-empezar)
3. [Paso a paso: instalación](#paso-1-instalar-python)
4. [Paso a paso: configurar Google](#paso-2-configurar-google-cloud)
5. [Paso a paso: descargar el programa](#paso-3-descargar-el-programa)
6. [Paso a paso: primera ejecución](#paso-4-correr-el-programa-por-primera-vez)
7. [¿Cómo lo uso todos los días?](#cómo-lo-uso-todos-los-días)
8. [¿Qué significa el "score" de cada noticia?](#qué-significa-el-score)
9. [Problemas comunes y soluciones](#problemas-comunes)
10. [Glosario de términos](#glosario)

---

## ¿Para qué sirve?

Imaginá que trabajás en una ONG, un estudio de abogados, o una empresa del sector minero, y necesitás estar al tanto de todo lo que pasa con la minería en Argentina. Todos los días salen noticias nuevas en diarios de San Juan, Mendoza, Catamarca, Jujuy, etc.

**Sin este programa:**
- Tenés que entrar a 10 diarios diferentes todos los días
- Buscás "minería" en Google y te aparecen 500 resultados irrelevantes
- Perdés horas leyendo noticias que no te interesan
- Te enterás tarde de algo importante

**Con este programa:**
- El programa busca solo por vos
- Filtra las noticias y les pone un puntaje de 1 a 100
- Te arma una planilla ordenada de mejor a peor
- Te marca en verde las más importantes
- Funciona solo: lo podés programar para que corra todos los días a las 9 de la mañana

### ¿Qué noticias detecta?

El programa busca noticias sobre:
- **Proyectos mineros:** Pascua Lama, Veladero, Josemaría, Los Azules, El Pachón, etc.
- **Conflictos:** asambleas de vecinos, cortes de ruta, amparos judiciales
- **Legislación:** leyes de glaciares, leyes provinciales (7722, 5001, etc.)
- **Empresas:** Barrick, Yamana, McEwen, Lundin, BHP
- **Impacto ambiental:** estudios hidrogeológicos, cuencas hídricas
- **Litio:** salares, proyectos de litio en el norte

Y **descarta automáticamente** noticias sobre:
- Robos de cables (noticias policiales que mencionan "cobre")
- Delincuencia común
- Artículos genéricos que solo dicen "la minería es buena" sin datos concretos

---

## ¿Qué necesito antes de empezar?

| Requisito | ¿Para qué? | ¿Lo tengo? |
|-----------|-----------|------------|
| Una computadora con Windows, Mac o Linux | Para correr el programa | ✅ Seguro sí |
| Conexión a internet | Para buscar noticias y guardar en Google | ✅ Seguro sí |
| Una cuenta de Gmail | Para usar Google Sheets | ✅ Si tenés Gmail, ya está |
| Python instalado | El "motor" del programa | ❌ Hay que instalarlo |
| Credenciales de Google Cloud | Para que el programa pueda escribir en tu planilla | ❌ Hay que configurarlo |

**No necesitás saber programar.** Esta guía te lleva de la mano paso a paso.

---

## Paso 1: Instalar Python

Python es el "motor" que hace funcionar el programa. Es gratis y muy usado.

### En Windows:

1. Andá a [python.org/downloads](https://www.python.org/downloads/)
2. Hacé clic en el botón amarillo grande que dice **"Download Python"**
3. Se descarga un archivo `.exe`
4. Abrilo
5. **IMPORTANTE:** Marcá la casilla que dice **"Add Python to PATH"** (es chiquita, está abajo)
6. Hacé clic en **"Install Now"**
7. Esperá a que termine

### En Mac:

1. Andá a [python.org/downloads](https://www.python.org/downloads/)
2. Hacé clic en **"Download Python"**
3. Se descarga un archivo `.pkg`
4. Abrilo y seguí los pasos como cualquier instalador de Mac

### Verificar que se instaló bien:

1. Abrí la terminal (en Windows buscá "cmd"; en Mac buscá "Terminal")
2. Escribí esto y apretá Enter:
   ```
   python --version
   ```
3. Debería aparecer algo como `Python 3.12.0` o similar. Si aparece, ¡listo!

---

## Paso 2: Configurar Google Cloud

Esto suena complicado pero no lo es. Es como darle una "llave" al programa para que pueda escribir en tu planilla de Google Sheets.

### 2.1 Crear un proyecto en Google Cloud

1. Andá a [console.cloud.google.com](https://console.cloud.google.com/)
2. Si te pide iniciar sesión, usá tu cuenta de Gmail
3. Arriba a la izquierda dice **"Select a project"** — hacé clic ahí
4. Apretá **"New Project"**
5. Poné un nombre, por ejemplo: `scraper-mineria`
6. Apretá **"Create"**
7. Esperá unos segundos a que se cree

### 2.2 Habilitar las APIs necesarias

El programa necesita "permiso" para usar Google Sheets y Google Drive.

1. En el menú de la izquierda, hacé clic en **"APIs & Services"** → **"Library"**
2. En el buscador, escribí **"Google Sheets API"**
3. Hacé clic en el resultado y apretá **"Enable"**
4. Volvemos a la biblioteca: hacé clic en **"APIs & Services"** → **"Library"** de nuevo
5. Buscá **"Google Drive API"**
6. Hacé clic y apretá **"Enable"**

### 2.3 Crear una cuenta de servicio

Esto crea un "usuario robot" que el programa usará para conectarse.

1. En el menú izquierdo, andá a **"APIs & Services"** → **"Credentials"**
2. Arriba apretá **"+ Create Credentials"**
3. Elegí **"Service Account"**
4. En **"Service Account Name"** poné: `scraper-andino`
5. En **"Service Account ID"** se completa solo
6. Apretá **"Create and Continue"**
7. En **"Role"** seleccioná **"Editor"** (está en el desplegable)
8. Apretá **"Continue"**
9. Apretá **"Done"**

### 2.4 Crear la llave (archivo JSON)

1. Seguís en **"Credentials"**
2. En la lista, hacé clic en `scraper-andino` (el que acabás de crear)
3. Arriba, andá a la pestaña **"Keys"**
4. Apretá **"+ Add Key"** → **"Create New Key"**
5. Elegí **JSON**
6. Apretá **"Create"**
7. **Se descarga un archivo automáticamente.** Guardalo en un lugar seguro. No lo pierdas.

### 2.5 Renombrar y mover el archivo

1. Encontrá el archivo descargado. Tiene un nombre largo tipo `scraper-mineria-123456.json`
2. Renombralo a **`creds.json`**
3. Este archivo es tu "llave". No lo compartas con nadie.

---

## Paso 3: Descargar el programa

### 3.1 Descargar todos los archivos

Necesitás estos archivos en una carpeta en tu computadora. Creá una carpeta llamada `scraper_andino` en tu Escritorio.

Dentro de esa carpeta, creá estas subcarpetas:
- `src/`
- `tests/`
- `config/`

### 3.2 Archivos que necesitás descargar

**Archivos principales** (van en la carpeta raíz `scraper_andino/`):

| Archivo | ¿Dónde va? | ¿Qué hace? |
|---------|-----------|------------|
| `main.py` | Carpeta raíz | Es el "botón de encendido" del programa |
| `requirements.txt` | Carpeta raíz | Lista de cosas que hay que instalar |
| `README.md` | Carpeta raíz | Esta guía |
| `.gitignore` | Carpeta raíz | Le dice a git qué no subir |
| `LICENSE` | Carpeta raíz | La licencia del programa |

**Archivos de código** (van en `scraper_andino/src/`):

| Archivo | ¿Qué hace? |
|---------|-----------|
| `__init__.py` | Dice que `src` es un paquete de Python |
| `config.py` | Acá están todas las configuraciones (provincias, términos, etc.) |
| `utils.py` | Limpia el texto de las noticias (saca mayúsculas, acentos, etc.) |
| `scoring.py` | El "cerebro": calcula qué tan relevante es cada noticia |
| `scraper.py` | Busca las noticias en Google News |
| `sheets_client.py` | Guarda todo en Google Sheets |

**Archivos de tests** (van en `scraper_andino/tests/`):

| Archivo | ¿Qué prueba? |
|---------|-------------|
| `test_config.py` | Que la configuración funcione bien |
| `test_utils.py` | Que la limpieza de texto funcione |
| `test_scoring.py` | Que el puntaje de las noticias sea correcto |
| `test_scraper.py` | Que la búsqueda de noticias funcione |
| `test_sheets.py` | Que la conexión con Google Sheets funcione |

### 3.3 Mover el archivo de credenciales

Tomá el archivo `creds.json` que descargaste antes y ponelo en:
```
scraper_andino/config/creds.json
```

**IMPORTANTE:** El archivo `creds.json` contiene tu llave privada. Nunca lo subas a internet. El archivo `.gitignore` ya está configurado para ignorarlo automáticamente.

---

## Paso 4: Instalar las dependencias

Las "dependencias" son programas chicos que el scraper necesita para funcionar. Es como cuando instalás un juego y te pide instalar DirectX.

1. Abrí la terminal (cmd en Windows, Terminal en Mac)
2. Andá hasta la carpeta del programa. Escribí:
   ```
   cd Desktop/scraper_andino
   ```
   (Si la pusiste en otro lado, cambiá "Desktop" por la ruta correcta)
3. Escribí esto y apretá Enter:
   ```
   pip install -r requirements.txt
   ```
4. Esperá a que termine. Va a instalar varias cosas (numpy, scikit-learn, gspread, etc.)
5. Si te pregunta algo, apretá "y" y Enter.

---

## Paso 5: Correr el programa por primera vez

### 5.1 Verificar que todo esté en orden

En la terminal, asegurate de estar en la carpeta del programa:
```
cd Desktop/scraper_andino
```

### 5.2 Correr los tests (opcional pero recomendado)

Los tests son como un "control de calidad" que verifica que todo funciona bien.

```
pytest tests/ -v
```

Debería decir algo como:
```
============================== 30 passed in 2.5s ==============================
```

Si dice "passed", ¡todo está perfecto!

### 5.3 Correr el programa

```
python main.py
```

**¿Qué debería pasar?**

1. Va a aparecer texto en la terminal como:
   ```
   2026-07-19 09:30:00 | INFO     | scraper_andino.main | Iniciando Scraper Andino v2.0.0
   2026-07-19 09:30:01 | INFO     | scraper_andino.scraper | Escaneando San Juan...
   2026-07-19 09:30:02 | INFO     | scraper_andino.scraper | Procesando 15 entradas de San Juan
   ```

2. El programa va a buscar noticias de todas las provincias, una por una.

3. Al final va a decir algo como:
   ```
   2026-07-19 09:30:25 | INFO     | scraper_andino.sheets | 12 noticias nuevas guardadas
   ```

4. **¡Listo!** Ahora andá a tu Google Drive y buscá una planilla llamada **"Monitoreo Mineria Argentina"**.

### 5.4 Ver tu planilla

1. Abrí [drive.google.com](https://drive.google.com)
2. Buscá la planilla "Monitoreo Mineria Argentina"
3. Hacé clic para abrirla
4. Vas a ver columnas: título, fecha, medio, autor, descripción, url, score
5. La columna de score tiene colores: **verde oscuro** = muy relevante, **blanco** = poco relevante

---

## ¿Cómo lo uso todos los días?

### Opción A: Correrlo manualmente

1. Abrí la terminal
2. Andá a la carpeta: `cd Desktop/scraper_andino`
3. Escribí: `python main.py`
4. Esperá a que termine
5. Revisá tu planilla

### Opción B: Programarlo para que corra solo (Windows)

Si querés que corra automáticamente todos los días a las 9 AM:

1. Buscá "Task Scheduler" en el menú de Windows
2. Apretá "Create Basic Task"
3. Nombre: `Scraper Andino`
4. Trigger: `Daily`
5. Start: `09:00:00`
6. Action: `Start a program`
7. Program: buscá `python.exe` (generalmente está en `C:\\Users\\TU_NOMBRE\\AppData\\Local\\Programs\\Python\\Python312\\python.exe`)
8. Add arguments: `main.py`
9. Start in: la ruta completa a tu carpeta `scraper_andino` (ej: `C:\\Users\\TU_NOMBRE\\Desktop\\scraper_andino`)
10. Apretá "Finish"

### Opción C: Programarlo para que corra solo (Mac/Linux)

1. Abrí la terminal
2. Escribí: `crontab -e`
3. Agregá esta línea al final:
   ```
   0 9 * * * cd /Users/TU_NOMBRE/Desktop/scraper_andino && python main.py >> /Users/TU_NOMBRE/Desktop/scraper_andino/log.txt 2>&1
   ```
4. Guardá y cerrá (en nano: Ctrl+O, Enter, Ctrl+X)

---

## ¿Qué significa el "score"?

El score es un número del **1 al 100** que indica qué tan relevante es la noticia para vos.

| Score | Color | Significado | Ejemplo |
|-------|-------|-------------|---------|
| 90-100 | 🟢 Verde oscuro | **Muy relevante** | Noticia sobre un nuevo proyecto minero, conflicto socioambiental, ley de glaciares |
| 70-89 | 🟢 Verde claro | **Relevante** | Noticia técnica sobre extracción, reservas, inversión |
| 50-69 | 🟡 Amarillo | **Moderadamente relevante** | Menciona minería pero es más general |
| 30-49 | 🟠 Naranja | **Poco relevante** | Noticia económica que menciona minería de pasada |
| 1-29 | ⚪ Blanco | **Mínimamente relevante** | Casi no tiene que ver, pero pasó el filtro mínimo |

### ¿Cómo se calcula?

El programa mira tres cosas:

1. **Similitud con temas importantes:** ¿La noticia habla de "proyecto de cobre", "lixiviación", "Veladero", etc.? Más palabras técnicas = más puntos.

2. **Densidad técnica:** ¿Cuántas palabras del glosario minero aparecen? Pero con un límite para evitar que alguien "haga trampa" repitiendo palabras.

3. **Penalizaciones:**
   - Si aparecen palabras como "robo de cables" o "delincuentes" → **score 0** (se descarta)
   - Si la noticia solo dice cosas vagas como "la minería es buena" sin datos → se le bajan puntos
   - Si es de un medio andino especializado (Diario de Cuyo, El Tribuno, etc.) → **+15 puntos de bono**

---

## Problemas comunes

### "No se encontró 'creds.json'"

**Solución:** El archivo de credenciales no está en el lugar correcto. Asegurate de que esté en:
```
scraper_andino/config/creds.json
```

### "ModuleNotFoundError: No module named 'gspread'"

**Solución:** No instalaste las dependencias. En la terminal, andá a la carpeta del programa y ejecutá:
```
pip install -r requirements.txt
```

### "SpreadsheetNotFound"

**Solución:** El programa no encuentra la planilla. Esto es normal la primera vez: el programa la crea automáticamente. Si la borraste de Google Drive, volvé a correr el programa y la va a recrear.

### "Error fetching feed, reintentando..."

**Solución:** Google News está tardando en responder. El programa va a intentar de nuevo automáticamente (hasta 3 veces). Si sigue fallando, esperá unos minutos y probá de nuevo.

### "0 noticias captadas"

**Solución:** Puede ser que:
- No haya noticias nuevas en las últimas 24 horas (raro pero posible)
- Google News cambió algo en su RSS (el programa se adapta solo, pero a veces hay que esperar)
- Tu internet no funciona bien

Probá de nuevo en una hora.

### La planilla no se actualiza

**Solución:**
1. Andá a Google Drive
2. Buscá "Monitoreo Mineria Argentina"
3. Si existe pero está vacía, probablemente es la primera vez y no había noticias nuevas
4. Si no existe, el programa la va a crear la próxima vez que corra

---

## Glosario

| Término | Significado |
|---------|-------------|
| **API** | Una "puerta" que permite que dos programas se comuniquen. En este caso, entre nuestro programa y Google Sheets. |
| **Backoff** | Esperar cada vez más tiempo entre intentos cuando algo falla. Primero 2 segundos, después 4, después 8... |
| **Credenciales** | Tu "llave" para acceder a Google Sheets. Es un archivo JSON que descargás de Google Cloud. |
| **Dataclass** | Una forma de organizar datos en Python. En este caso, la configuración del programa. |
| **Deduplicación** | Evitar que la misma noticia aparezca dos veces en la planilla. |
| **Feed RSS** | Un formato de datos que usan los sitios de noticias para compartir sus artículos. |
| **Glosario técnico** | Lista de palabras específicas del sector minero que el programa busca. |
| **Keyword stuffing** | Truco de hacer trampa repitiendo muchas palabras clave para subir el puntaje. El programa tiene un límite para evitarlo. |
| **Logging** | Sistema de "diario" que anota todo lo que hace el programa, útil para saber qué pasó si algo falla. |
| **Rate limiting** | Esperar un tiempo entre requests para no sobrecargar el servidor de Google. |
| **Score** | Puntaje del 1 al 100 que indica qué tan relevante es una noticia. |
| **Scraper** | Programa que "raspa" información de internet automáticamente. |
| **Semillas positivas** | Frases modelo que representan noticias que nos interesan. |
| **TF-IDF** | Técnica matemática para medir qué tan importante es una palabra en un texto. |
| **Token** | Una "contraseña temporal" que Google te da para acceder a sus servicios. |

---

## 📞 ¿Necesitás ayuda?

Si algo no funciona:

1. **Revisá esta guía de nuevo** — muchos problemas tienen solución acá
2. **Mirá los mensajes de error** en la terminal — suelen decir exactamente qué pasó
3. **Corré los tests:** `pytest tests/ -v` — te van a decir si algo está roto
4. **Verificá que `creds.json` esté en `config/`** — es el problema más común

---

## 📝 Licencia

Este programa es de código abierto (licencia MIT). Podés usarlo, modificarlo y compartirlo libremente. Lo único que pedimos es que si hacés mejoras, las compartas con la comunidad.

---

**Hecho con ❤️ para monitorear la minería en Argentina de forma transparente.**
