"""
Módulo encargado de resolver el CAPTCHA presente en la página de la Registraduría.

Este componente utiliza técnicas de procesamiento de imágenes (OpenCV + Pillow)
y el motor de reconocimiento óptico de caracteres (Tesseract OCR) para intentar
leer el texto del captcha automáticamente.

Si no logra obtener un texto confiable después de varios intentos, se devuelve
`None` para que el flujo principal permita el ingreso manual.

Fecha: 2025-11-02
"""
from selenium.webdriver.common.by import By
from PIL import Image, ImageOps
from src import utils
import cv2
import numpy as np
import io
import time
import pytesseract

# Ruta local del ejecutable de Tesseract OCR.
# Ajusta esta ruta según tu instalación local si no coincide.
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def resolver_captcha(driver, max_intentos=1):
    """
    Intenta resolver el captcha de la Registraduría utilizando Tesseract OCR.

    El proceso incluye:
        - Capturar la imagen del captcha directamente desde el navegador.
        - Convertirla a escala de grises.
        - Aplicar técnicas de limpieza (umbral binario y morfología) para mejorar la legibilidad.
        - Ejecutar OCR con configuración ajustada para letras mayúsculas y números.
        - Validar el texto extraído según su longitud y formato.

    Args:
        driver (webdriver): Instancia activa de Selenium con la página cargada.
        max_intentos (int, opcional): Número máximo de intentos de resolución antes
            de rendirse y devolver None. Por defecto es 1.

    Returns:
        str | None: Texto del captcha si se detecta correctamente,
        o `None` si el OCR no logra extraer un resultado confiable.
    """
    for intento in range(1, max_intentos + 1):
        print(f"\n🧠 Resolviendo captcha (intento {intento}/{max_intentos})...")

        # ---------------------------------------------------------------------
        # Capturar la imagen del captcha directamente desde el navegador
        # ---------------------------------------------------------------------
        captcha_element = driver.find_element(By.ID, utils.id_campo_captcha)
        captcha_png = captcha_element.screenshot_as_png
        image = Image.open(io.BytesIO(captcha_png))


        # ---------------------------------------------------------------------
        # Preprocesamiento de imagen para mejorar precisión de OCR
        # ---------------------------------------------------------------------
        gray = ImageOps.grayscale(image)
        img_cv = np.array(gray)
        _, thresh = cv2.threshold(img_cv, 150, 255, cv2.THRESH_BINARY)  # No invertimos
        kernel = np.ones((1, 1), np.uint8)
        img_clean = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        final_image = Image.fromarray(img_clean)


        # ---------------------------------------------------------------------
        # Reconocimiento de texto mediante Tesseract
        # ---------------------------------------------------------------------
        config = "--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        text = pytesseract.image_to_string(final_image, config=config).strip().replace(" ", "")
        text = ''.join(filter(str.isalnum, text.upper()))

        print(f"🔎 Captcha detectado: '{text}'")


        # ---------------------------------------------------------------------
        # Validar si el texto detectado parece confiable
        # ---------------------------------------------------------------------
        if 4 <= len(text) <= 8 and text.isalnum():
            return text

        print("Captcha no confiable, recargando imagen...")
        try:
            driver.find_element(By.XPATH, utils.xpath_boton_recargar_captcha).click()
        except:
            print("⚠️ No se encontró botón para refrescar el captcha.")
        time.sleep(2)

    # -------------------------------------------------------------------------
    # Si se agotan los intentos, retornar None para ingreso manual
    # -------------------------------------------------------------------------
    print("OCR no logró resolver el captcha automáticamente.")
    return None