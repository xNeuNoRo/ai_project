from pathlib import Path

# Importamos las rutas y funciones necesarias para configurar los directorios y formatos de salida del proyecto.
from src.base.rutas import (
    RAIZ_PROYECTO,
    DIR_DATA,
    DIR_DATA_RAW,
    DIR_DATA_INTERIM,
    DIR_DATA_PROCESSED,
    DIR_OUTPUTS,
    DIR_OUTPUTS_TABLAS,
    DIR_OUTPUTS_GRAFICOS,
    DIR_OUTPUTS_REPORTES,
    DIR_OUTPUTS_MODELOS,
    DIR_NOTEBOOKS,
    DIR_TESTS,
    asegurar_directorios,
    obtener_ruta_dataset as construir_ruta_dataset,
    obtener_ruta_salida as construir_ruta_salida,
    listar_directorios_base,
)

# ==========================================================
# Configuración general del proyecto
# ==========================================================
# Aquí definimos constantes y funciones relacionadas con la configuración general del proyecto,
# como los nombres de archivos por defecto, formatos de salida, y funciones para obtener rutas específicas
# según el tipo de dato o resultado que queremos guardar.
NOMBRE_DATASET_POR_DEFECTO = "dataset"
EXTENSION_DATASET_POR_DEFECTO = "csv"

FORMATO_TABLAS_POR_DEFECTO = "csv"
FORMATO_GRAFICOS_POR_DEFECTO = "png"
FORMATO_REPORTES_POR_DEFECTO = "md"
FORMATO_MODELOS_POR_DEFECTO = "joblib"

DIR_RAIZ_PROYECTO = RAIZ_PROYECTO

DIR_DATOS = DIR_DATA
DIR_DATOS_RAW = DIR_DATA_RAW
DIR_DATOS_INTERIM = DIR_DATA_INTERIM
DIR_DATOS_PROCESSED = DIR_DATA_PROCESSED

DIR_SALIDAS = DIR_OUTPUTS
DIR_SALIDAS_TABLAS = DIR_OUTPUTS_TABLAS
DIR_SALIDAS_GRAFICOS = DIR_OUTPUTS_GRAFICOS
DIR_SALIDAS_REPORTES = DIR_OUTPUTS_REPORTES
DIR_SALIDAS_MODELOS = DIR_OUTPUTS_MODELOS

DIR_CUADERNOS = DIR_NOTEBOOKS
DIR_TESTS_UNITARIOS = DIR_TESTS

# ==========================================================
# Compatibilidad temporal con el código actual
# Estas variables permiten refactorizar por etapas sin romper
# los módulos que todavía usan nombres anteriores.
# ==========================================================

BASE_DIR = DIR_RAIZ_PROYECTO

RAW_DATA_DIR = DIR_DATOS_RAW
INTERIM_DATA_DIR = DIR_DATOS_INTERIM
PROCESSED_DATA_DIR = DIR_DATOS_PROCESSED

# Alias temporal para no romper el código viejo
CLEAN_DATA_DIR = DIR_DATOS_PROCESSED

OUTPUTS_DIR = DIR_SALIDAS
TABLAS_DIR = DIR_SALIDAS_TABLAS
GRAFICOS_DIR = DIR_SALIDAS_GRAFICOS
REPORTES_DIR = DIR_SALIDAS_REPORTES
MODELOS_DIR = DIR_SALIDAS_MODELOS

# Rutas de archivos por defecto para el dataset principal
RAW_FILE = construir_ruta_dataset(
    nombre_dataset=NOMBRE_DATASET_POR_DEFECTO,
    etapa="raw",
    extension=EXTENSION_DATASET_POR_DEFECTO,
)

# Ruta de archivo por defecto para el dataset limpio (processed)
CLEAN_FILE = construir_ruta_dataset(
    nombre_dataset=f"{NOMBRE_DATASET_POR_DEFECTO}_clean",
    etapa="processed",
    extension=EXTENSION_DATASET_POR_DEFECTO,
)

# ==========================================================
# Funciones auxiliares de configuración
# ==========================================================

# Funcion auxiliar para asegurar la estructura de directorios del proyecto
# Que en realidad es como un alias, ya que solo llama la de asegurar_directorios
def asegurar_estructura_proyecto() -> None:
    """
    Crea la estructura base de directorios del proyecto si no existe.
    """
    asegurar_directorios()

# ==========================================================
# Funciones para obtener rutas específicas 
# según el tipo de dato o resultado que queremos guardar
# ==========================================================

# Estas funciones permiten centralizar la lógica de construcción de rutas y formatos, facilitando cambios futuros sin tener que modificar el código en múltiples lugares.
def obtener_ruta_datos(
    nombre_dataset: str | None = None,
    etapa: str = "raw",
    extension: str | None = None,
) -> Path:
    """
    Devuelve la ruta esperada para un dataset según su nombre, etapa y extensión.

    Parámetros
    ----------
    nombre_dataset : str | None
        Nombre lógico del dataset. Si no se pasa, usa el nombre por defecto.
    etapa : str
        'raw', 'interim' o 'processed'.
    extension : str | None
        Extensión del archivo. Si no se pasa, usa la extensión por defecto.
    """
    return construir_ruta_dataset(
        nombre_dataset=nombre_dataset or NOMBRE_DATASET_POR_DEFECTO,
        etapa=etapa,
        extension=extension or EXTENSION_DATASET_POR_DEFECTO,
    )


# Esta función es similar a obtener_ruta_datos pero para rutas de salida, con lógica adicional para formatos por defecto según el tipo de resultado.
def obtener_ruta_salida_config(
    nombre_archivo: str,
    tipo: str = "tablas",
    subcarpeta: str | None = None,
    extension: str | None = None,
) -> Path:
    """
    Devuelve una ruta de salida dentro de outputs.

    Parámetros
    ----------
    nombre_archivo : str
        Nombre base del archivo.
    tipo : str
        'tablas', 'graficos', 'reportes' o 'modelos'.
    subcarpeta : str | None
        Subcarpeta opcional para organizar resultados.
    extension : str | None
        Extensión de salida. Si no se pasa, se asigna una por defecto según el tipo.
    """
    if extension is None:
        extensiones_por_tipo = {
            "tablas": FORMATO_TABLAS_POR_DEFECTO,
            "graficos": FORMATO_GRAFICOS_POR_DEFECTO,
            "reportes": FORMATO_REPORTES_POR_DEFECTO,
            "modelos": FORMATO_MODELOS_POR_DEFECTO,
        }
        extension = extensiones_por_tipo.get(tipo, "txt")

    return construir_ruta_salida(
        nombre_archivo=nombre_archivo,
        tipo=tipo,
        subcarpeta=subcarpeta,
        extension=extension,
    )


# Función para obtener un diccionario con los directorios base del proyecto, útil para acceder a ellos de forma centralizada.
def obtener_directorios_base() -> dict[str, Path]:
    """
    Devuelve un diccionario con los directorios base del proyecto.
    """
    return listar_directorios_base()