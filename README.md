# Scraper Inteligente de Megaminería en Argentina (Corredor Andino)

Este proyecto es un pipeline de datos automatizado que extrae, audita semánticamente y clasifica noticias sobre la actividad minera en las provincias andinas de Argentina. Los resultados se exportan en tiempo real a una hoja de cálculo de Google Sheets optimizada visualmente.

## 🛠️ Estructura del Proyecto

*   `main.py`: Código principal del scraper y procesamiento de datos.
*   `requirements.txt`: Librerías de Python requeridas.
*   `creds.json`: Credenciales de la Cuenta de Servicio de Google Cloud (Debe ser generado por el usuario, **no se sube a GitHub**).

## 🚀 Instalación y Uso

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/TU_USUARIO/scraper-minero-argentina.git](https://github.com/TU_USUARIO/scraper-minero-argentina.git)
    cd scraper-minero-argentina
    ```

2.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurar credenciales:**
    *   Coloca tu archivo `creds.json` de Google Cloud en la carpeta raíz del proyecto.
    *   Comparte tu Google Sheet con el correo de la cuenta de servicio (`client_email` dentro del JSON) otorgándole permisos de **Editor**.

4.  **Ejecutar el Scraper:**
    ```bash
    python main.py
    ```
