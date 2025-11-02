"""
Módulo utilitario con constantes y configuraciones base para la automatización.

Este archivo contiene las constantes globales que se utilizan en los procesos de scraping
y automatización del sistema de consulta de certificados de cédula de ciudadanía
en la página de la Registraduría Nacional del Estado Civil de Colombia.

Fecha: 2025-11-02
"""

# Lista de meses del año (en minúsculas y en español)
meses=["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"]

#  URL principal de la página de consulta
url_page = "https://certvigenciacedula.registraduria.gov.co/Datos.aspx"

# Identificadores y XPaths de los elementos usados en la automatización Selenium
id_campo_cedula="ContentPlaceHolder1_TextBox1"

# XPaths para los botones principales
xpath_boton_continuar="//input[@id='ContentPlaceHolder1_Button1' and @value='Continuar']"
xpath_boton_generar_certificado = "//input[@id='ContentPlaceHolder1_Button1' and @value='Generar Certificado']"

# XPath que verifica la aparición del mensaje de confirmación previo a la generación del certificado
xpath_texto_confirmacion_certificado  ="//*[contains(text(),'La certificación se expedira para el numero de cédula')]"

# XPath del botón que permite recargar el CAPTCHA
xpath_boton_recargar_captcha="//*[@title='Change the code']"

# Identificadores de los campos del formulario de fecha de expedición
id_select_campo_dia="ContentPlaceHolder1_DropDownList1"
id_select_campo_mes="ContentPlaceHolder1_DropDownList2"
id_select_campo_year="ContentPlaceHolder1_DropDownList3"

# Campos asociados al CAPTCHA
id_campo_captcha="datos_contentplaceholder1_captcha1_CaptchaImage"
id_campo_codigo="ContentPlaceHolder1_TextBox2"








