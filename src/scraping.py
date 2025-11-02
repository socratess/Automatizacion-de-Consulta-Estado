"""
Módulo encargado de automatizar la consulta del certificado de cédula.

Este archivo contiene la lógica principal del scraping:
- Accede a la página oficial de consulta.
- Llena los campos del formulario (cédula, fecha de expedición, captcha).
- Intenta resolver el captcha automáticamente (usando OCR).
- Si falla, solicita el ingreso manual del código.
- Descarga y gestiona el PDF resultante.
- Guarda la información extraída en la base de datos y archivos estructurados.

Fecha: 2025-11-02
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from src.storage import guardar_informacion_extraida
from src.configuration import abrir_enlace, esperar_obtener_documento, cerrar_driver
from selenium.webdriver.support import expected_conditions as EC
from src.orc import resolver_captcha
from src import utils
from src.pdf_parser import gestionar_pdf
import time




def consultar_certificado_cedula(driver,numero_cedula,dia_expedicion_cedula,mes_expedicion_cedula,year_expedicion_cedula):
    """
    Ejecuta el proceso completo de scraping en la página de consulta de certificados de cédula.

    Pasos principales:
        1. Abre la página de consulta usando Selenium.
        2. Completa los campos del formulario (número de cédula y fecha de expedición).
        3. Intenta resolver el captcha automáticamente (máx. 2 intentos).
        4. Si no logra resolverlo, solicita ingreso manual del captcha.
        5. Descarga el certificado PDF.
        6. Procesa el PDF y guarda la información extraída.

    Args:
        driver (webdriver): Instancia activa del navegador Selenium.
        numero_cedula (str): Número de cédula ingresado por el usuario.
        dia_expedicion_cedula (str): Día de expedición de la cédula (dos dígitos).
        mes_expedicion_cedula (str): Nombre del mes de expedición (en minúsculas, español).
        year_expedicion_cedula (str): Año de expedición de la cédula (cuatro dígitos).

    Returns:
        dict | None: Diccionario con rutas de almacenamiento si el proceso fue exitoso.
            Ejemplo:
            {
                "db": "ruta/a/identifier.sqlite",
                "json": "ruta/a/resultado.json"
            }
            Retorna None si ocurre algún error o si el captcha no se resuelve correctamente.
    """
    try:
        # --- Abrir página y preparar espera explícita ---
        abrir_enlace(driver)
        wait = WebDriverWait(driver, 60)

        # Esperar que el campo del captcha sea visible
        captcha=wait.until(EC.visibility_of_element_located((By.ID,utils.id_campo_captcha)))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth',block: 'center'});", captcha)

        # --- Completar formulario de datos personales ---
        cedula=driver.find_element(By.ID,utils.id_campo_cedula)
        cedula.clear()
        cedula.send_keys(numero_cedula)

        Select(driver.find_element(By.ID,utils.id_select_campo_dia)).select_by_value(dia_expedicion_cedula)
        Select(driver.find_element(By.ID, utils.id_select_campo_mes)).select_by_visible_text(mes_expedicion_cedula.capitalize())
        Select(driver.find_element(By.ID, utils.id_select_campo_year)).select_by_value(year_expedicion_cedula)

        # ---------------------------------------------------------------------
        # Intentar resolver captcha automáticamente (máximo 2 intentos)
        # ---------------------------------------------------------------------
        captcha_correcto = False
        for intento in range(1, 3):
            print(f"\n🧠 Intentando resolver captcha automáticamente (intento {intento}/2)...")

            captcha_text = resolver_captcha(driver)
            if not captcha_text:
                print("⚠️ No se pudo obtener texto del captcha. Reintentando...")
                continue

            # Ingresar el texto del captcha detectado
            cod_imagen = driver.find_element(By.ID, utils.id_campo_codigo)
            cod_imagen.clear()
            cod_imagen.send_keys(captcha_text)
            driver.find_element(By.XPATH, utils.xpath_boton_continuar).click()
            time.sleep(2)

            # Verificar si apareció una alerta indicando error en captcha
            try:
                alert = driver.switch_to.alert
                mensaje = alert.text.strip()
                alert.accept()
                print(f"❌ Captcha incorrecto: {mensaje}")

                # Intentar refrescar el captcha
                try:
                    driver.find_element(By.XPATH, utils.xpath_boton_recargar_captcha).click()
                    time.sleep(2)
                except:
                    print("⚠️ No se pudo refrescar el captcha automáticamente.")
                continue
            except:
                captcha_correcto = True
                break


        # ---------------------------------------------------------------------
        # Si no se logra resolver automáticamente, permitir ingreso manual
        # ---------------------------------------------------------------------
        if not captcha_correcto:
            print("\n🚫 No se logró resolver el captcha automáticamente.")
            captcha_text = input("👉 Ingresa manualmente el captcha que ves en pantalla: ")

            cod_imagen = driver.find_element(By.ID, utils.id_campo_codigo)
            cod_imagen.clear()
            cod_imagen.send_keys(captcha_text)
            driver.find_element(By.XPATH, utils.xpath_boton_continuar).click()
            time.sleep(2)

        # ---------------------------------------------------------------------
        # Esperar que aparezca el botón para generar certificado
        # ---------------------------------------------------------------------
        try:
            wait.until(EC.visibility_of_element_located((By.XPATH, utils.xpath_boton_generar_certificado)))
            print("✅ Captcha validado correctamente. Procediendo a generar certificado...")
        except:
            print("⚠️ No se detectó el botón 'Generar certificado'. Puede que el captcha haya fallado.")
            return None

        # ---------------------------------------------------------------------
        # Descargar y procesar el certificado PDF
        # ---------------------------------------------------------------------
        driver.find_element(By.XPATH,utils.xpath_boton_generar_certificado).click()
        result = guardar_informacion_extraida(gestionar_pdf(esperar_obtener_documento(driver.download_dir)))
        if not result:
            print("⚠️ No se pudo gestionar correctamete la información del PDF.")
            return None
        return result


    except Exception as ex:
        print(f" Error durante el proceso de scraping del documento en la página: {ex}")
    finally:
        # Cerrar el navegador al finalizar el proceso
        cerrar_driver(driver)