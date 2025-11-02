"""
Módulo de generación de documentos PDF de prueba.

Este módulo crea archivos PDF de ejemplo que simulan los certificados
de cédula emitidos por la Registraduría, con el fin de probar el flujo
completo del sistema (lectura, extracción, almacenamiento).

Utiliza la librería `reportlab` para generar los documentos.

Fecha: 2025-11-02
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from uuid import uuid4
from datetime import datetime
import os

def crear_pdf(ruta_dir):
    """
      Genera un PDF de prueba con información simulada de un certificado de cédula.

      El documento se crea con un nombre único basado en la fecha y un UUID,
      y se guarda dentro del directorio especificado.

      Args:
          ruta_dir (str): Ruta del directorio donde se guardará el archivo PDF.

      Returns:
          str: Ruta absoluta del archivo PDF creado.

      Ejemplo:
          >>> ruta = crear_pdf("data/pdfs")
          >>> print(ruta)
          'C:/Users/.../data/pdfs/test_20251102__153045__abc12345.pdf'
      """
    actual_time=datetime.now().strftime("%Y%m%d__%H%M%S__")
    ruta_pdf = os.path.abspath(os.path.join(ruta_dir, f"test_{actual_time}_{str(uuid4())[:12]}.pdf"))

    create_doc= canvas.Canvas(ruta_pdf,pagesize=letter)
    create_doc.setFont("Times-Roman",15)

    create_doc.drawString(100,740,"CERTIFICADO DE PRUEBA DE CÉDULA DE CIUDADANÍA")
    create_doc.drawString(100, 680, "Cédula de Ciudadanía: 0.000.000.000")
    create_doc.drawString(100, 650, "Fecha de Expedición: 31 DE DICIEMBRE DE 2020")
    create_doc.drawString(100, 620, "Lugar de Expedición: MOSQUERA - CUNDINAMARCA")
    create_doc.drawString(100, 590, "A nombre de: NOMBRE PRUEBA TESTING")
    create_doc.drawString(100, 560, "Estado: VIGENTE")

    create_doc.save()

    print(f"PDF de prueba creado en: {ruta_pdf}")
    return ruta_pdf

def crear_pdf_vacio(ruta_dir):
    """
        Crea un archivo PDF vacío (sin contenido de texto) para pruebas negativas.

        Este PDF puede utilizarse para probar el comportamiento del sistema
        cuando se intenta procesar un documento sin texto extraíble.

        Args:
            ruta_dir (str): Ruta del directorio donde se guardará el PDF vacío.

        Returns:
            str: Ruta absoluta del archivo PDF vacío generado.

        Ejemplo:
            >>> ruta_vacio = crear_pdf_vacio("data/pdfs")
            >>> print(ruta_vacio)
            'C:/Users/.../data/pdfs/test_vacio_abc12345.pdf'
        """
    ruta_pdf_vacio = os.path.abspath(os.path.join(ruta_dir, f"test_vacio_{str(uuid4())[:12]}.pdf"))

    doc_vac = canvas.Canvas(ruta_pdf_vacio)
    doc_vac.showPage()
    doc_vac.save()
    return ruta_pdf_vacio
