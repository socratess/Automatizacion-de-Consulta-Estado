"""
Módulo de pruebas de integración del flujo completo de consulta y extracción.

Evalúa la interacción de los módulos principales:
    - `pdf_parser.py`     → lectura y análisis del documento PDF descargado.
    - `storage.py`        → persistencia de resultados en base de datos y JSON.

Casos principales:
    - Validación del manejo de errores o descarga fallida.
    - Consistencia de datos almacenados entre SQLite y JSON.
    - Limpieza y cierre correcto de recursos.

Recomendación:
    Ejecutar con `python -m unittest test/test_integracion_flujo_completo.py -v`
"""

from src.create_pdf import crear_pdf
from src.pdf_parser import gestionar_pdf
from src.storage import guardar_informacion_extraida
import tempfile
import unittest
import os
import json
import sqlite3
import HtmlTestRunner



class Test_Integration_Flujo_Completo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.nv_dir_temp = tempfile.TemporaryDirectory()
        print(f"Directorio temporal: {cls.nv_dir_temp.name}")

        cls.pdf_ruta = crear_pdf(cls.nv_dir_temp.name)
        print(f"Se creó el pdf con información para prueba: {cls.pdf_ruta}")

        cls.base_dt_dir_ruta = os.path.join(cls.nv_dir_temp.name, 'db')
        os.makedirs(cls.base_dt_dir_ruta, exist_ok=True)
        cls.base_dt_ruta = os.path.join(cls.base_dt_dir_ruta, 'informacion.db')

        cls.json_ruta = os.path.join(cls.nv_dir_temp.name, 'json')
        os.makedirs(cls.json_ruta, exist_ok=True)



    @classmethod
    def tearDownClass(cls):
        cls.nv_dir_temp.cleanup()
        print(f"Directorio temporal y su contenido elimiando: {cls.nv_dir_temp.name}")


    def test_flujo_completo_pdf_extraccion_a_almacenamiento(self):
        print("[Test] Ejecutando flujo completo PDF_extracción_almacenamiento")

        print("[Test] Ejecutando la extracción")
        data_pdf_ext=gestionar_pdf(self.pdf_ruta)

        self.assertIsInstance(data_pdf_ext,dict,"No tiene el formato necesitado de ser dict")
        self.assertNotIn("error",data_pdf_ext,"No tiene informacion el Pdf")

        print("[Test] Ejecutando el almacenamiento")
        data_alm=guardar_informacion_extraida(data_pdf_ext,self.nv_dir_temp.name)
        self.assertIn('db',data_alm,"No tiene informacion en la base de datos")
        self.assertIn('json',data_alm,"No tiene informacion en el json")

        self.assertTrue(os.path.exists(data_alm.get('db')),"La base de datos no existe")
        self.assertTrue(os.path.exists(data_alm.get('json')),"El json no existe")

        con = sqlite3.connect(data_alm.get('db'))
        cr=con.cursor()
        cr.execute("SELECT * from informacion ORDER BY id DESC LIMIT 1")
        dt_db=cr.fetchone()
        cr.execute("SELECT * from informacion")
        dt_all_db=cr.fetchall()
        con.close()

        self.assertGreaterEqual(len(dt_all_db),1,"No tiene informacion en la base de datos")
        self.assertEqual(len(dt_db),7,"La base de datos no existe")
        self.assertEqual(dt_db[1],data_pdf_ext["cedula_ciudadania"],"La base de datos no tiene datos correctos")
        self.assertEqual(dt_db[6],data_pdf_ext["estado_cedula"],"La base de datos no tiene datos correctos")

        with open(data_alm.get('json'),"r",encoding="utf-8") as f:
            json_data=json.load(f)

        self.assertEqual(json_data.get("cedula_ciudadania"),data_pdf_ext["cedula_ciudadania"],"El json no tiene datos correctos")
        self.assertEqual(json_data.get("estado_cedula"),data_pdf_ext["estado_cedula"],"El json no tiene datos correctos")

        print("[Test][OK] Flujo completo ejecutado y verificado correctamente")

if __name__ == '__main__':
    ruta_report = os.path.join(os.path.dirname(__file__), "reports")
    unittest.main(
        testRunner=HtmlTestRunner.HTMLTestRunner(
            output=ruta_report,
            report_title='Resultados_Test_PDF_Extraccion_Y_Almacenamiento_Flujo_Completo',
            combine_reports=True,
            add_timestamp=True,
            verbosity=2
        )
    )
