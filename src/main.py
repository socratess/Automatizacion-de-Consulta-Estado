"""
Módulo principal del sistema de scraping para la consulta de certificados de cédula.

Este script actúa como punto de entrada del programa. Permite al usuario ingresar manualmente
los datos necesarios (número de cédula y fecha de expedición), valida la información,
crea el controlador (driver) para el navegador y ejecuta el proceso de scraping para
consultar, descargar y almacenar los resultados.

Fecha: 2025-11-02
"""
from datetime import datetime
from src.scraping import consultar_certificado_cedula
from src.configuration import crear_driver
from src import utils
import locale

# ---------------------------------------------------------------------------
# Configuración inicial del entorno
# ---------------------------------------------------------------------------

# Se obtiene la fecha actual del sistema
fecha_actual = datetime.today()

# Configura el idioma y formato local para usar nombres de meses en español
locale.setlocale(locale.LC_TIME, "es_CO.UTF-8")

# ---------------------------------------------------------------------------
# Funciones principales
# ---------------------------------------------------------------------------

def establecer_datos():
    """
    Controla el flujo principal de entrada de datos y ejecución del scraping.

    1. Solicita los datos del usuario (número de cédula y fecha de expedición).
    2. Valida que la fecha no sea futura.
    3. Crea el driver de Selenium.
    4. Ejecuta la función de scraping con los datos proporcionados.

    Returns:
        dict: Diccionario con las rutas generadas tras la consulta.
            Ejemplo:
            {
                "db": "ruta/a/identifier.sqlite",
                "json": "ruta/a/resultado.json"
            }
    """
    # Solicita los datos de entrada al usuario
    data_obtenida=obtener_datos_usuarios()
    # Convierte la fecha ingresada a objeto datetime
    fecha_ingresada = datetime.strptime(data_obtenida["dia_expedicion_cedula"]+" "+data_obtenida["mes_expedicion_cedula"]+" "+data_obtenida["year_expedicion_cedula"],"%d %B %Y")

    # Valida que la fecha no sea posterior a la actual
    while fecha_ingresada.date() > fecha_actual.date():
       data_obtenida=obtener_datos_usuarios()
       fecha_ingresada = datetime.strptime(
           data_obtenida["dia_expedicion_cedula"] + " " + data_obtenida["mes_expedicion_cedula"] + " " + data_obtenida[
               "year_expedicion_cedula"], "%d %B %Y")

    # Crea el controlador del navegador y ejecuta el scraping
    driver = crear_driver()
    return consultar_certificado_cedula(driver,**data_obtenida)

def obtener_datos_usuarios():
    """
    Solicita e interactúa con el usuario para obtener y validar los datos necesarios.

    Returns:
        dict: Diccionario con los datos de entrada validados.
            {
                "numero_cedula": str,
                "dia_expedicion_cedula": str,
                "mes_expedicion_cedula": str,
                "year_expedicion_cedula": str
            }
    """
    year_actual = fecha_actual.year
    # Solicitud del número de cédula
    number_cedula=input("Ingresar numero de cedula: ").lower()
    while not number_cedula.isdigit() or len(number_cedula)>10:
        print("Solo se permiten números (máximo 10 dígitos).")
        number_cedula = input("Ingresar numero de cedula: ")

    # Solicitud del día de expedición
    dia_fecha_expedicion=(input("Ingresar dia de expedicion: ")).lower()
    while not dia_fecha_expedicion.isdigit() or len(dia_fecha_expedicion)!=2 or 1 > int(dia_fecha_expedicion) or int(dia_fecha_expedicion)>31:
        print("Día inválido. Ingrese un número entre 01 y 31.")
        dia_fecha_expedicion=input("Ingresar dia de expedicion: ")

    # Solicitud del mes de expedición
    mes_fecha_expedicion=(input("Ingresar mes de expedicion: ")).lower()
    while not mes_fecha_expedicion.isalpha() or not mes_fecha_expedicion in utils.meses:
        print(f"Mes inválido.")
        mes_fecha_expedicion=input("Ingresar mes de expedicion: ")

    # Solicitud del año de expedición
    year_fecha_expedicion=(input("Ingresar año de expedicion: ")).lower()
    while not year_fecha_expedicion.isdigit() or len(year_fecha_expedicion)!=4 or int(year_fecha_expedicion)>year_actual:
        print("Año inválido. Debe ser numérico de 4 dígitos y no mayor al actual.")
        year_fecha_expedicion=input("Ingresar año de expedicion: ")

    return {"numero_cedula":number_cedula, "dia_expedicion_cedula":dia_fecha_expedicion, "mes_expedicion_cedula":mes_fecha_expedicion, "year_expedicion_cedula":year_fecha_expedicion}


# ---------------------------------------------------------------------------
# Ejecución directa del programa
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    """
       Bloque de ejecución principal.

       - Llama a la función `establecer_datos()`.
       - Muestra las rutas generadas si la consulta fue exitosa.
       - En caso contrario, notifica un posible error.
       """
    resultado = establecer_datos()
    if len(resultado)>0:
           if resultado["db"]:
               print(f'Ruta de la base de datos: {resultado["db"]}')
           if resultado["json"]:
               print(f'Ruta del json: {resultado["json"]}')
    else:
        print("No hay rutas, disponibles por error con el Pdf")
