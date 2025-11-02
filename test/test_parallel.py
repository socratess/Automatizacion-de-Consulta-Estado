"""
Módulo de pruebas paralelas para la ejecución distribuida de los casos de prueba.

Este archivo permite ejecutar varios escenarios de prueba en paralelo con el fin
de optimizar tiempos y validar la robustez del flujo bajo múltiples ejecuciones
simultáneas.

Casos principales:
    - Ejecución simultánea de consultas a la Registraduría.
    - Validación de independencia entre sesiones de descarga.
    - Control de errores en procesos concurrentes.

Recomendación:
    Ejecutar con `python -m unittest test/test_parallel.py -v`
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from src.scraping import consultar_certificado_cedula
from src.configuration import crear_driver, fecha_aleatorio
from src.create_pdf import crear_pdf
import time
import random
import unittest


MODO_SIMULACION = True
NUM_CONSULTAS = 15
HILOS = 5


class Test_Parallel(unittest.TestCase):

    def realizar_consulta(self, id_prueba, cedula):
        """
        Ejecuta una consulta (real o simulada) midiendo tiempo y resultado.
        """
        inicio = time.perf_counter()

        try:
            if MODO_SIMULACION:
                # -----------------------------
                # 🔹 Modo simulado: se procesa PDF falso
                # -----------------------------
                from src.pdf_parser import gestionar_pdf
                from src.storage import guardar_informacion_extraida
                import tempfile

                with tempfile.TemporaryDirectory() as temp_dir:
                    pdf_prueba = crear_pdf(temp_dir)
                    rutas_guardadas = guardar_informacion_extraida(gestionar_pdf(pdf_prueba),temp_dir)



                duracion_simulacion = round(random.uniform(1.5, 4.0), 2)
                time.sleep(duracion_simulacion)

                return {
                    "id_prueba": id_prueba,
                    "cedula": cedula,
                    "resultado": "ok (simulado)",
                    "tiempo": duracion_simulacion,
                    "json": rutas_guardadas.get("json"),
                    "db": rutas_guardadas.get("db")
                }

            # -----------------------------
            # 🔹 Modo real: usa scraping real
            # -----------------------------
            driver = crear_driver()
            dia, mes, year = fecha_aleatorio()
            resultado = consultar_certificado_cedula(driver, cedula, dia, mes, year)
            duracion = round(time.perf_counter() - inicio, 2)

            return {
                "id_prueba": id_prueba,
                "cedula": cedula,
                "resultado": 'ok' if resultado else 'falló',
                "tiempo": duracion
            }

        except Exception as ex:
            return {
                "id_prueba": id_prueba,
                "cedula": cedula,
                "resultado": 'error',
                "error": str(ex)
            }

    def test_consulta_cedula_paralela(self):
        """
        Ejecuta 15 consultas paralelas y mide desempeño.
        """
        import os, json
        from datetime import datetime

        cedulas_prueba = [f'10{i:08}' for i in range(1, NUM_CONSULTAS + 1)]
        resultados = []

        print(f"\n🧪 Iniciando {NUM_CONSULTAS} consultas paralelas "
              f"({'simuladas' if MODO_SIMULACION else 'reales'})...\n")

        inicio_total = time.perf_counter()

        with ThreadPoolExecutor(max_workers=HILOS) as executor:
            futures = [
                executor.submit(self.realizar_consulta, i, cedula)
                for i, cedula in enumerate(cedulas_prueba, start=1)
            ]
            for future in as_completed(futures):
                resultado = future.result()
                resultados.append(resultado)
                print(f" → Consulta {resultado['id_prueba']} ({resultado['cedula']}) "
                      f": {resultado['resultado']} en {resultado.get('tiempo', '?')}s")

        duracion_total = round(time.perf_counter() - inicio_total, 2)
        exitos = sum(1 for r in resultados if 'ok' in r['resultado'])
        errores = len(resultados) - exitos

        print(f"\n📊 Resultado final:")
        print(f"   - Consultas exitosas: {exitos}")
        print(f"   - Consultas con error: {errores}")
        print(f"   - Tiempo total: {duracion_total} segundos\n")

        # 🔍 Validaciones finales
        self.assertEqual(len(resultados), NUM_CONSULTAS, "No se ejecutaron todas las consultas.")
        self.assertTrue(exitos >= int(NUM_CONSULTAS * 0.8),
                        "Más del 20% de las consultas fallaron.")

        # 🗂️ Guardar reporte JSON resumido
        reporte = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "modo": "simulado" if MODO_SIMULACION else "real",
            "consultas_totales": NUM_CONSULTAS,
            "consultas_exitosas": exitos,
            "consultas_con_error": errores,
            "tiempo_total_segundos": duracion_total,
            "detalles": resultados
        }



        # Crear carpeta si no existe
        ruta_reporte = os.path.join("test", "reports", f"reporte_parallel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        os.makedirs(os.path.dirname(ruta_reporte), exist_ok=True)

        # Guardar en archivo JSON
        with open(ruta_reporte, "w", encoding="utf-8") as f:
            json.dump(reporte, f, indent=4, ensure_ascii=False)

        print(f"🗂️ Reporte guardado en: {ruta_reporte}\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
