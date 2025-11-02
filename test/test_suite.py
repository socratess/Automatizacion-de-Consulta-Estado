"""
Archivo principal de suite de pruebas unitarias e integradas.

Este módulo reúne y organiza la ejecución de todos los tests disponibles en la
carpeta `test/` para facilitar la validación completa del proyecto mediante
un solo comando.

Incluye:
    - Pruebas unitarias individuales (funciones de extracción y almacenamiento en`src/`).
    - Pruebas de integración (flujo completo de extracción y almacenamiento).

Recomendación:
    Ejecutar con `python -m unittest discover -s test -v`
"""

from test.test_pdf_extraccion import Test_Pdf_Extraccion
from test.test_storage import Test_Storage_Pdf
from test.test_integration_flujo_completo import Test_Integration_Flujo_Completo
import unittest
import os
import HtmlTestRunner

class Test_Suite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("..... Iniciando suite de pruebas completas (extracción + almacenamiento) .....")

    def test_all(self):
        self.assertTrue(True)

    @classmethod
    def tearDownClass(cls):
        print("..... Suite de pruebas finalizada .....")

if __name__ == '__main__':
    carga = unittest.TestLoader()
    suite  = unittest.TestSuite()
    suite.addTest(carga.loadTestsFromTestCase(Test_Pdf_Extraccion))
    suite.addTest(carga.loadTestsFromTestCase(Test_Storage_Pdf))
    suite.addTest(carga.loadTestsFromTestCase(Test_Integration_Flujo_Completo))

    ruta_report = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(ruta_report, exist_ok=True)


    runner=HtmlTestRunner.HTMLTestRunner(
            output=ruta_report,
            report_name='Suite_Resultados_Tests_PDF_Extraccion_Y_Almacenamiento_Unitarios_Y_Flujo_Completo',
            combine_reports=True,
            add_timestamp=True,
            report_title='Suite - Resultados Tests PDF: Extraccion Y Almacenamiento (Unitarios y flujo completo)',
            verbosity=2
        )

    runner.run(suite)
