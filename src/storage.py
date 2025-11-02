"""
Módulo de almacenamiento de información extraída.

Este módulo gestiona el guardado de los datos procesados desde los certificados
en formato PDF, almacenándolos tanto en una base de datos SQLite como en un
archivo JSON estructurado.

Fecha: 2025-11-02
"""
import json
import os
import sqlite3
from datetime import datetime
from uuid import uuid4

def guardar_informacion_extraida(informacion, result_dir=None):
    """
        Guarda la información extraída de un PDF en formato JSON y SQLite.

        Esta función centraliza el proceso de almacenamiento, asegurando que la
        información sea guardada tanto en un archivo `.json` como en una base
        de datos SQLite. Si el directorio de resultados no existe, lo crea
        automáticamente.

        Args:
            informacion (dict): Diccionario con los datos extraídos del PDF.
            result_dir (str, optional): Directorio donde guardar los resultados.
                Si no se especifica, se crea automáticamente en `data/results/`.

        Returns:
            dict: Diccionario con las rutas de los archivos generados:
                {
                    "db": "ruta/a/informacion.db",
                    "json": "ruta/a/informacion.json"
                }

        Ejemplo:
            >>> datos = {"cedula_ciudadania": "12345678", "nombre_ciudadano": "Juan Pérez"}
            >>> guardar_informacion_extraida(datos)
            {'db': '.../data/results/informacion.db', 'json': '.../data/results/20251102_...json'}
        """
    try:
        if result_dir is None:
            result_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "results"))
        os.makedirs(result_dir, exist_ok=True)
        db_path= os.path.join(result_dir, 'informacion.db')

        db_data=gestionar_base_de_datos(db_path,informacion)
        json_data=gestionar_json(informacion,result_dir)
        return {'db':db_data,'json':json_data}
    except Exception as ex:
        print(f"Error al guardar informacion: {ex}")
        return {'error': str(ex)}
def gestionar_base_de_datos(db_path,informacion):
    """
        Inserta los datos en una base de datos SQLite.

        Si la base de datos no existe, la crea con la estructura necesaria.
        Luego inserta un nuevo registro con la información del ciudadano.

        Args:
            db_path (str): Ruta del archivo de base de datos SQLite.
            informacion (dict): Diccionario con los datos extraídos del PDF.

        Returns:
            str | dict: Ruta del archivo SQLite si tiene éxito, o un dict con error.

        Ejemplo:
            >>> gestionar_base_de_datos("data/results/informacion.db", info)
            'C:/.../data/results/informacion.db'
        """
    try:
        conn = sqlite3.connect(db_path, timeout=10)
        cursor = conn.cursor()
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS informacion
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           cedula
                           TEXT,
                           nombre
                           TEXT,
                           fecha_expedida
                           TEXT,
                           municipio_expedida
                           TEXT,
                           departamento_expedida
                           TEXT,
                           estado_cedula
                           TEXT
                       )
                       ''')

        cursor.execute('''
                       INSERT INTO informacion (cedula, nombre, fecha_expedida, municipio_expedida, departamento_expedida,
                                                estado_cedula)
                       values (?, ?, ?, ?, ?, ?)
                       ''', (
                           informacion.get('cedula_ciudadania'),
                           informacion.get('nombre_ciudadano'),
                           informacion.get('fecha_expedida'),
                           informacion.get('municipio_expedida'),
                           informacion.get('departamento_expedida'),
                           informacion.get('estado_cedula'),
                       ))
        conn.commit()
        conn.close()
        print(f'Informacion Ingresada en la base de datos SQLite: {db_path}')
        return db_path
    except Exception as e:
        print(f'Error en la gestión de la base de datos SQLite: {e}')
        return {'error': str(e)}
def gestionar_json(informacion,result_dir):
    """
       Guarda la información extraída en un archivo JSON con nombre único.

       El archivo se nombra utilizando la fecha, hora y UUID parcial para evitar
       colisiones entre diferentes ejecuciones.

       Args:
           informacion (dict): Datos extraídos del certificado.
           result_dir (str): Ruta del directorio donde se guardará el archivo JSON.

       Returns:
           str | dict: Ruta del archivo JSON si tiene éxito, o un dict con error.

       Ejemplo:
           >>> gestionar_json(info, "data/results")
           'C:/.../data/results/20251102_12345678_Juan_Perez_abc123.json'
       """
    try:
        ts = datetime.now().strftime("%d%m%Y %H%M%S")
        ced = informacion.get('cedula_ciudadania') or "no tiene"
        nom = informacion.get('nombre_ciudadano') or "no tiene"
        json_nombre = f'{ts}_{ced}_{nom}_{str(uuid4())[:12]}.json'
        json_ruta = os.path.join(result_dir, json_nombre)
        with open(json_ruta, 'w', encoding='utf-8') as f:
            json.dump(informacion, f, ensure_ascii=False, indent=4)
        print(f'Informacion de respaldo JSON: {json_ruta}')
        return json_ruta
    except Exception as e:
        print(f'Error en la gestión del json: {e}')
        return {'error': str(e)}