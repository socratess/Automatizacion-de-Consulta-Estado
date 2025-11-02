"""
Módulo de pruebas unitarias para `src/pdf_parser.py`.

Evalúa las funciones responsables de la lectura, extracción y parseo de texto
desde documentos PDF obtenidos del portal de la Registraduría.

Casos principales:
    - Extracción correcta de texto en documentos PDF válidos.
    - Detección y manejo de PDFs vacíos o ilegibles.
    - Parseo de información clave: número de cédula, nombre, fecha, lugar y estado.
    - Validación del formato final de los datos obtenidos.

Recomendación:
    Ejecutar con `python -m unittest test/test_pdf_extraccion.py -v`
"""

from src.pdf_parser import gestionar_pdf,parsear_documento_pdf,leer_documento_pdf
from src.create_pdf import crear_pdf, crear_pdf_vacio
import os
import HtmlTestRunner
import tempfile
import unittest

class Test_Pdf_Extraccion(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
       cls.nv_dir_temp = tempfile.TemporaryDirectory()
       print(f"Directorio temporal: {cls.nv_dir_temp.name}")

       cls.pdf_ruta =crear_pdf(cls.nv_dir_temp.name)
       cls.pdf_vacio_ruta = crear_pdf_vacio(cls.nv_dir_temp.name)
       print(f"Se creó el pdf con información para prueba: {cls.pdf_ruta}")
       print(f"Se creó el pdf vacio para prueba: {cls.pdf_vacio_ruta}")

    @classmethod
    def tearDownClass(cls):
        cls.nv_dir_temp.cleanup()
        print(f"Directorio temporal y su contenido elimiando: {cls.nv_dir_temp.name}")

    def test_crear_pdf(self):
        print("[Test]... Crear pdf")
        self.assertTrue(os.path.exists(self.pdf_ruta), "No existe el pdf")

    def test_leer_documento_pdf(self):
        print("[Test]... Validando lectura del pdf")

        self.doc = leer_documento_pdf(self.pdf_ruta)

        self.assertIsInstance(self.doc, str, "No es el formato requerido")
        self.assertTrue(self.doc,"Esta vacio, hay información")

    def test_parsear_documento_pdf(self):
        print("[Test]... Validando parsear del pdf")

        self.data=parsear_documento_pdf(leer_documento_pdf(self.pdf_ruta))

        self.assertIsInstance(self.data, dict, "No es el formato requerido")
        self.assertTrue(self.data,"Esta vacio, hay información")

    def test_gestionar_pdf(self):
        print("[Test]... Validando gestionar pdf")

        self.result=gestionar_pdf(self.pdf_ruta)

        self.assertIsInstance(self.result, dict, "No es el formato requerido")
        self.assertTrue(self.result,"Esta vacio, hay información")
        self.assertIn("cedula_ciudadania", self.result,"No se tiene el número del documento")
        self.assertIn("nombre_ciudadano", self.result,"No se tiene el nombre del dueño del documento")
        self.assertIn("fecha_expedida", self.result,"No se tiene la fecha de expedición del documento")
        self.assertIn("municipio_expedida", self.result,"No se tiene el municipio del documento")
        self.assertIn("departamento_expedida", self.result, "No se tiene el departamento del documento")
        self.assertIn("estado_cedula", self.result,"No se tiene el estado del documento")
        self.assertEqual(self.result["estado_cedula"],'Vigente', "No esta vigente")
        self.assertTrue(self.result["cedula_ciudadania"].isdigit(), "Error, No es contiene solo digitos")
        self.assertIn("-",self.result.get("fecha_expedida"))

    def  test_pdf_vacio(self):
        print("[Test]... Validando vacio")

        self.data_vac=gestionar_pdf(self.pdf_vacio_ruta)
        self.assertTrue(os.path.exists(self.pdf_ruta), "No existe el pdf")
        self.assertIsInstance(self.data_vac,dict, "No es el formato requerido")
        self.assertIn("error",self.data_vac,"No se tiene la gestion del error")



if __name__ == '__main__':
    ruta_report = os.path.join(os.path.dirname(__file__), "reports")
    unittest.main(
        testRunner=HtmlTestRunner.HTMLTestRunner(
            output=ruta_report,
            report_title='Resultados_Test_PDF_Extraccion',
            combine_reports=True,
            add_timestamp=True,
            verbosity=2
        )
    )
