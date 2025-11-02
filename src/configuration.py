"""
Módulo de configuración del entorno Selenium y manejo de rutas de descarga.

Este archivo centraliza la configuración del navegador Chrome, la gestión
de directorios temporales para descargas PDF, y utilidades generales
para ejecutar y controlar pruebas de scraping o automatización.

Incluye:
    - Configuración dinámica del WebDriver (Chrome)
    - Creación y control del directorio de descargas
    - Espera activa para detectar archivos PDF descargados
    - Funciones de soporte (abrir, cerrar navegador y generar fechas aleatorias)

Fecha: 2025-11-02
"""
from time import time, sleep
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from src import utils
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import os
import uuid
import glob
import random

def esperar_obtener_documento(ruta_descarga):
    """
    Espera hasta que se detecte un archivo PDF descargado en una carpeta.

    Esta función monitorea la carpeta de descargas configurada para el
    navegador, verificando periódicamente si el archivo PDF ha terminado
    de descargarse. Si se detecta un archivo `.crdownload`, espera hasta
    que desaparezca antes de devolver la ruta final del PDF.

    Args:
        ruta_descarga (str): Ruta completa al directorio donde se descargan los archivos PDF.

    Returns:
        str | None: Ruta absoluta del PDF más reciente descargado, o `None`
        si no se detecta ningún PDF después del tiempo máximo de espera (40s).
    """
    print("Esperando finalizar la descarga del PDF...")

    inicio  = time()
    while time() - inicio < 40:
        if any ( i.endswith('.crdownload') for i in os.listdir(ruta_descarga)):
            sleep(1)
            continue

        # Buscar archivos PDF completados
        pdf_archivo = glob.glob(os.path.join(ruta_descarga, '*.pdf'))
        if pdf_archivo:
            pdf_archivo.sort(key=os.path.getmtime, reverse=True)
            ruta_pdf = pdf_archivo[0]
            print("Documento obtenido en la descarga: ", os.path.basename(ruta_pdf))
            return ruta_pdf
        sleep(2)
    print("No se detectó PDF a tiempo.")
    return None

def obtener_ruta_descarga():
    """
     Genera y crea dinámicamente una carpeta de descargas única por sesión.

     La carpeta se guarda dentro de `data/pdfs/` y lleva un nombre único
     con la siguiente estructura:
         `session__YYYYMMDD__HHMMSS__UUID`

     Esto facilita la organización de archivos descargados por ejecución
     o sesión del bot.

     Returns:
         str: Ruta absoluta de la carpeta de descarga recién creada.
     """
    actual_dir = os.path.dirname(os.path.abspath(__file__))
    descarga_basico = os.path.abspath(os.path.join(actual_dir,"..","data","pdfs"))
    os.makedirs(descarga_basico,exist_ok=True)

    ids_session= datetime.now().strftime("%Y%m%d__%H%M%S__")+str(uuid.uuid4())[:12]
    descarga_dir = os.path.join(descarga_basico,f"session__{ids_session}")
    os.makedirs(descarga_dir,exist_ok=True)

    return descarga_dir

def crear_driver():
    """
       Crea e inicializa una instancia de navegador Chrome configurada
       para descargas automáticas de archivos PDF.

       Utiliza `webdriver_manager` para instalar automáticamente la versión
       adecuada del controlador (ChromeDriver).

       Returns:
           webdriver.Chrome: Instancia del navegador configurada con las
           preferencias necesarias para descargar archivos PDF sin intervención.
       """
    print("Creando navegador...")

    ruta_descarga = obtener_ruta_descarga()

    chrome_options = Options()
    prefs = {
        "download.default_directory": ruta_descarga,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.download_dir = ruta_descarga
    driver.maximize_window()
    print(f"Descargas configuradas en: {driver.download_dir}")
    return driver

def abrir_enlace(driver):
    """
      Abre la página principal del proceso automatizado definida en `utils.url_page`.

      Args:
          driver (webdriver.Chrome): Instancia activa del navegador Selenium.
      """
    print(f"Abriendo página: {utils.url_page}")
    driver.get(utils.url_page)

def cerrar_driver(driver):
    """
       Cierra de manera segura la instancia del navegador Chrome abierta por Selenium.

       Args:
           driver (webdriver.Chrome): Instancia activa del navegador Selenium.
       """
    print("Cerrando navegador...")
    driver.quit()

def fecha_aleatorio():
    """
        Genera una fecha aleatoria simple (día, mes, año).

        Esta función se utiliza principalmente para pruebas o formularios
        donde se requiere simular fechas de nacimiento u otros campos de
        fecha en contextos de automatización.

        Returns:
            tuple[str, str, str]: Tupla con el formato `(día, mes, año)`.
        """
    dias = [str(i) for i in range(1,28)]
    years=[ str(i) for i in range(1994,2024)]

    return random.choice(dias), random.choice(utils.meses), random.choice(years)