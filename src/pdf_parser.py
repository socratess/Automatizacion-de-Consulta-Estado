"""
Módulo para lectura y análisis de certificados PDF de cédulas de ciudadanía.

Este módulo utiliza `pdfplumber` para extraer texto desde archivos PDF descargados,
y posteriormente analiza el contenido para obtener datos estructurados como
número de cédula, nombre, fecha, lugar de expedición y estado del documento.

Flujo general:
    1. `leer_documento_pdf()` abre y extrae texto de un archivo PDF.
    2. `parsear_documento_pdf()` interpreta el texto y extrae los campos relevantes.
    3. `gestionar_pdf()` combina ambos pasos y devuelve un diccionario con los datos finales.

Fecha: 2025-11-02
"""
import pdfplumber

def leer_documento_pdf(pdf_ruta):
    """
    Lee el contenido textual de un archivo PDF utilizando `pdfplumber`.

    Args:
        pdf_ruta (str): Ruta completa del archivo PDF a leer.

    Returns:
        str: Texto completo concatenado de todas las páginas del PDF.
        Si ocurre un error o el archivo no tiene texto legible, devuelve una cadena vacía.
    """
    texto=""
    try:
        with pdfplumber.open(pdf_ruta) as pdf:
            for page in pdf.pages:
                texto += page.extract_text()+'\n' if page.extract_text() else ''
        return texto
    except Exception as e:
        print(f'Se tiene el error con la lectura del pdf: {e}')
        return ""
def parsear_documento_pdf(texto_pdf):
    """
       Interpreta el texto extraído del PDF y estructura los datos relevantes.

       Este método busca líneas clave que comienzan con etiquetas conocidas como:
       - 'Cédula de ciudadanía'
       - 'Fecha de expedición'
       - 'Lugar de expedición'
       - 'A nombre de'
       - 'Estado'

       Args:
           texto_pdf (str): Texto plano extraído previamente desde el archivo PDF.

       Returns:
           dict: Diccionario con los campos principales extraídos. Ejemplo:
               {
                   "cedula_ciudadania": "1234567890",
                   "nombre_ciudadano": "Juan Pérez",
                   "fecha_expedida": "29-marzo-2011",
                   "municipio_expedida": "Bogotá",
                   "departamento_expedida": "Cundinamarca",
                   "estado_cedula": "Vigente"
               }

       Raises:
           Exception: Si el texto no cumple el formato esperado o falla el parseo.
       """
    try:
        datos_finales={ "cedula_ciudadania":None,
                        "nombre_ciudadano":None,
                        "fecha_expedida":None,
                        "municipio_expedida":None,
                        "departamento_expedida":None,
                        "estado_cedula":None
                       }
        for linea in texto_pdf.splitlines():
            linea = linea.strip().lower()

            if linea.startswith("cédula de ciudadanía"):datos_finales["cedula_ciudadania"]=linea.split(":")[-1].strip().replace(".","")

            elif linea.startswith("fecha de expedición"):datos_finales["fecha_expedida"] =linea.split(":")[-1].strip().replace(" de ","-")

            elif linea.startswith("lugar de expedición"):
                 lugar =(linea.split(":")[-1].strip()).split(" - ")
                 datos_finales["municipio_expedida"],datos_finales["departamento_expedida"]=lugar[0].capitalize(),lugar[1].capitalize()

            elif linea.startswith("a nombre de"): datos_finales["nombre_ciudadano"]= linea.split(":")[-1].strip().title()

            elif linea.startswith("estado"): datos_finales["estado_cedula"]= linea.split(":")[-1].strip().capitalize()

        return datos_finales
    except Exception as e:
        print(f"No se puede parsear el documento, se tiene error: {e}")
def gestionar_pdf(pdf_ruta):
    """
       Procesa completamente un archivo PDF: lectura, validación y parseo de información.

       Combina `leer_documento_pdf()` y `parsear_documento_pdf()` en una única función
       que se encarga de manejar errores y validar si el PDF contiene texto legible.

       Args:
           pdf_ruta (str): Ruta completa del archivo PDF que se desea procesar.

       Returns:
           dict: Diccionario con la información extraída del PDF o un mensaje de error.
               Ejemplo:
                   {"error": "Pdf sin texto para lectura"}  # si no se pudo extraer texto
       """
    print("Gestionando documento Pdf...")
    try:
        texto_pdf = leer_documento_pdf(pdf_ruta)
        if not texto_pdf.strip():
            print("No hay texto, pdf no contiene texto para lectura.")
            return {"error":"Pdf sin texto para lectura"}

        return parsear_documento_pdf(texto_pdf)
    except Exception as e:
        print(f'Error gestionando el pdf: {e}')
        return {"error":"Pdf no contiene texto para gestionar"}