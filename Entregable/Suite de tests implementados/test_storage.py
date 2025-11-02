"""
Módulo de pruebas unitarias para `src/storage.py`.

Verifica la correcta gestión y persistencia de la información extraída del
certificado de cédula en los formatos de salida esperados: base de datos SQLite
e información estructurada en archivos JSON.

Casos principales:
    - Creación y estructura de la base de datos `informacion.db`.
    - Inserción de registros válidos en SQLite.
    - Generación correcta de archivos JSON con contenido coherente.
    - Manejo de excepciones ante datos incompletos o errores de escritura.

Recomendación:
    Ejecutar con `python -m unittest test/test_storage.py -v`
"""

from src.storage import guardar_informacion_extraida, gestionar_json, gestionar_base_de_datos
import os
import tempfile
import json
import HtmlTestRunner
import sqlite3
import unittest


class Test_Storage_Pdf(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.nv_dir_temp=tempfile.TemporaryDirectory()

        cls.base_dt_dir_ruta=os.path.join(cls.nv_dir_temp.name, 'data_base')
        os.makedirs(cls.base_dt_dir_ruta, exist_ok=True)
        cls.base_dt_ruta = os.path.join(cls.base_dt_dir_ruta, 'informacion.db')
        cls.json_ruta=os.path.join(cls.nv_dir_temp.name, 'json')
        os.makedirs(cls.json_ruta, exist_ok=True)

        cls.data_pdf_prueba= {
            'cedula_ciudadania': '1111111111',
            'nombre_ciudadano': 'Nombre Prueba Testing',
            'fecha_expedida': '31-Diciembre-2020',
            'municipio_expedida': 'Funza',
            'departamento_expedida': 'Cundinamarca',
            'estado_cedula': 'Vigente'
        }

    @classmethod
    def tearDownClass(cls):
        cls.nv_dir_temp.cleanup()
        print(f"Directorio temporal eliminado con todo su contenido: {cls.nv_dir_temp.name}")

    def test_crear_json(self):
        print("[Test] Validando gestión de JSON...")
        json_result= gestionar_json(self.data_pdf_prueba,self.json_ruta)
        self.assertTrue(os.path.exists(json_result), "No existe el archivo json")

        with open(json_result,"r",encoding="utf-8") as file:
            data_json= json.load(file)
        self.assertIn("cedula_ciudadania",data_json,"No se tiene el elemento en el json")
        self.assertEqual(data_json['estado_cedula'],"Vigente","No tiene el elemento el valor correcto en el json")

    def test_crear_db(self):
        print("[Test] Validando gestión de base de datos...")
        db_result = gestionar_base_de_datos(self.base_dt_ruta,self.data_pdf_prueba)
        self.assertTrue(os.path.exists(db_result), "No existe el archivo db")

        test_conn = sqlite3.connect(db_result)
        cursor = test_conn.cursor()
        cursor.execute("SELECT * FROM informacion")
        data_db= cursor.fetchall()
        cursor.execute("SELECT * FROM informacion WHERE estado_cedula ='Vigente' ")
        data_estado_db=cursor.fetchall()
        test_conn.close()
        self.assertGreaterEqual(len(data_db),1,"No se tienen registros en la base de datos")
        self.assertTrue(data_estado_db,"No se tienen registros del estado de la cedula en la base de datos")

    def test_guardar_informacion_extraida(self):
        print("[Test] Validando guardado completo (DB + JSON)...")
        resultado_final=guardar_informacion_extraida(self.data_pdf_prueba,self.base_dt_dir_ruta)
        self.assertIsInstance(resultado_final,dict,"No es el formato requerido")
        self.assertTrue(resultado_final,"Esta vacio, hay informacion")
        self.assertTrue(os.path.exists(resultado_final.get("db")),"No existe el archivo db")
        self.assertTrue(os.path.exists(resultado_final.get('json')), "No existe el archivo json")
        self.assertIn("db",resultado_final,"No se tiene la ruta del archivo db")
        self.assertIn("json",resultado_final,"No se tiene la ruta del archivo json")

    def test_error_guardar_informacion(self):
        print("[Test] Validando manejo de error en guardar_informacion_extraida...")
        data_inc=None
        resultado=guardar_informacion_extraida(data_inc)
        self.assertIn("db",resultado,"No se tiene una correcta gestión de errores")
        self.assertIn("json",resultado, "No se tiene una correcta gestión de errores")
        self.assertIn("error", resultado.get('db'), "No se tiene una correcta gestión de errores")
        self.assertIn("error", resultado.get('json'), "No se tiene una correcta gestión de errores")
        self.assertIsInstance(resultado,dict,"No es el tipo correcto la respuesta")



if __name__ == '__main__':
    ruta_report = os.path.join(os.path.dirname(__file__), "reports")
    unittest.main(
        testRunner=HtmlTestRunner.HTMLTestRunner(
            output=ruta_report,
            report_title='Resultados_Test_Almacenamiento_PDF_Datos',
            combine_reports=True,
            add_timestamp=True,
            verbosity=2
        )
    )


