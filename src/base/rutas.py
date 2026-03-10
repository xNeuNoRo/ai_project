from pathlib import Path
from typing import Iterable

# ===========================
# Rutas del proyecto
# ===========================

# Este archivo vive en: src/base/rutas.py
# .resolve().parent -> src/base
# .parent.parent -> src
# .parent.parent.parent -> raíz del proyecto
# De esa forma tenemos la ruta absoluta a la raiz del proyecto,
# sin importar desde dónde se ejecute el código
RAIZ_PROYECTO = Path(__file__).resolve().parent.parent.parent

# ===========================
# Rutas de los directorios main
# ===========================

DIR_SRC = RAIZ_PROYECTO / "src"
DIR_DATA = RAIZ_PROYECTO / "data"
DIR_OUTPUTS = RAIZ_PROYECTO / "outputs"
DIR_NOTEBOOKS = RAIZ_PROYECTO / "notebooks"
DIR_TESTS = RAIZ_PROYECTO / "tests"

# ===========================
# Subdirectorios de data
# ===========================

DIR_DATA_RAW = DIR_DATA / "raw"
DIR_DATA_INTERIM = DIR_DATA / "interim"
DIR_DATA_PROCESSED = DIR_DATA / "processed"

# ===========================
# Subdirectorios de outputs/salidas/resultados
# ===========================

DIR_OUTPUTS_TABLAS = DIR_OUTPUTS / "tablas"
DIR_OUTPUTS_GRAFICOS = DIR_OUTPUTS / "graficos"
DIR_OUTPUTS_REPORTES = DIR_OUTPUTS / "reportes"
DIR_OUTPUTS_MODELOS = DIR_OUTPUTS / "modelos"

# ===========================
# Colecciones de directorios
# ===========================

DIRECTORIOS_BASE = [
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
]

# ===========================
# Funciones auxiliares
# ===========================


def asegurar_directorios(directorios: Iterable[Path] | None = None):
    """
    Crea los directorios recibidos si no existen.
    Si no se pasan directorios, crea la estructura base del proyecto.
    """

    # Definimos los directorios a crear, si no se pasa nada como arg,
    # entonces se crean los directorios base definidos en DIRECTORIOS_BASE
    directorios_a_crear = directorios or DIRECTORIOS_BASE

    # Ahora iteramos sobre cada una de las rutas y creamos los dirs
    # Solamente si es que no existen

    for directorio in directorios_a_crear:
        # El método mkdir de Path tiene un argumento parents que, si es True, crea también los directorios padres necesarios para llegar al directorio final
        # El argumento exist_ok, si es True, hace que no se lance un error si el directorio ya existe, simplemente lo ignora
        directorio.mkdir(parents=True, exist_ok=True)


def obtener_ruta_dataset(nombre_dataset: str, etapa: str = "raw", extension: str = "csv") -> Path:
    """
    Devuelve la ruta esperada para un dataset según su nombre y etapa.

    Parámetros
    ----------
    nombre_dataset : str
        Nombre lógico del dataset, por ejemplo:
        'inscritos_2006_2025' o 'egresados_2009_2025'

    etapa : str
        Puede ser: 'raw', 'interim' o 'processed'

    extension : str
        Extensión del archivo, por ejemplo '.csv' o '.xlsx'
    """

    # Normalizamos la etapa para evitar problemas con mayúsculas o espacios
    # strip() es el equivalente a un trim() en otros lenguajes
    etapa = etapa.lower().strip()

    # Definimos un diccionario que mapea cada etapa a su directorio correspondiente
    directorios_validos = {
        "raw": DIR_DATA_RAW,  # Aquí es donde se guardan los datasets originales, sin procesar
        "interim": DIR_DATA_INTERIM,  # Aquí es donde se guardan los datasets que han pasado por algún proceso de limpieza o transformación, pero que aún no están listos para el análisis final
        # Aquí es donde se guardan los datasets finales, listos para el análisis o modelado, después de haber pasado por todas las etapas de procesamiento necesarias
        "processed": DIR_DATA_PROCESSED,
    }

    # Validamos que la etapa sea una de las opciones válidas, si no lo es, lanzamos un error con un mensaje claro
    if etapa not in directorios_validos:
        raise ValueError(
            f"Etapa no válida: '{etapa}'. Usa 'raw', 'interim' o 'processed'."
        )

    # Normalizamos la extensión para asegurarnos de que empiece con un punto, por ejemplo '.csv' o '.xlsx'
    if not extension.startswith('.'):
        extension = f".{extension}"

    # Obtenemos el nombre completo del archivo con su extensión, por ejemplo 'inscritos_2006_2025.csv'
    nombre_archivo = f"{nombre_dataset}{extension}"

    # Finalmente, construimos la ruta completa combinando el directorio correspondiente a la etapa y el nombre del archivo, y la devolvemos
    # Ej: data/raw/inscritos_2006_2025.csv
    return directorios_validos[etapa] / nombre_archivo


def obtener_ruta_salida(nombre_archivo: str, tipo: str = "tablas", subcarpeta: str | None = None, extension: str = "csv") -> Path:
    """
    Construye una ruta de salida dentro de outputs.

    Parámetros
    ----------
    nombre_archivo : str
        Nombre base del archivo, sin ruta. Ejemplo: 'analisis_inscritos_2006_2025'

    tipo : str
        Puede ser: 'tablas', 'graficos', 'reportes' o 'modelos'

    subcarpeta : str | None
        Permite organizar salidas por dataset, fecha o análisis.
        Ej: 'egresados_2009_2025', '2024-09-01', 'analisis_inscritos'
        Todas carpetas donde se generarian los archivos relacionados a ese análisis o dataset.

    extension : str | None
        Si se indica, fuerza una extensión concreta.
        Ejemplo: '.csv', '.xlsx', '.png', '.md'
    """

    # Normalizamos el tipo para evitar problemas con mayúsculas o espacios
    tipo = tipo.lower().strip()

    # Definimos un diccionario que mapea cada tipo a su directorio correspondiente dentro de outputs
    directorios_validos = {
        # Aquí se guardan las tablas generadas, por ejemplo CSVs o Excel con datos procesados o resultados de análisis
        "tablas": DIR_OUTPUTS_TABLAS,
        # Aquí se guardan los gráficos generados, por ejemplo PNGs o SVGs con visualizaciones de los datos
        "graficos": DIR_OUTPUTS_GRAFICOS,
        # Aquí se guardan los reportes generados, por ejemplo archivos Markdown o PDFs con resúmenes y conclusiones del análisis
        "reportes": DIR_OUTPUTS_REPORTES,
        # Aquí se guardan los modelos entrenados, por ejemplo archivos Pickle o Joblib con modelos de machine learning listos para ser usados
        "modelos": DIR_OUTPUTS_MODELOS,
    }

    # Validamos que el tipo sea una de las opciones válidas, si no lo es, lanzamos un error con un mensaje claro
    if tipo not in directorios_validos:
        raise ValueError(
            f"Tipo de salida no válido: '{tipo}'. Usa 'tablas', 'graficos', 'reportes' o 'modelos'."
        )

    # Obtenemos el directorio base correspondiente al tipo de salida
    # Ej: si tipo es 'tablas', entonces directorio_base será DIR_OUTPUTS_TABLAS
    directorio_base = directorios_validos[tipo]

    # Si se especifica una subcarpeta, la añadimos al directorio base para organizar mejor las salidas relacionadas
    if subcarpeta:
        directorio_base = directorio_base / subcarpeta

    # Nos aseguramos de que el directorio base exista, si no existe lo creamos. Esto es importante para evitar errores al intentar guardar archivos en un directorio que no existe.
    directorio_base.mkdir(parents=True, exist_ok=True)

    # SI se proporciona una extension, normalizamos la extensión para asegurarnos de que empiece con un punto, por ejemplo '.csv' o '.png'
    if extension:
        if not extension.startswith('.'):
            extension = f".{extension}"
        # Y se la agregamos al nombre del archivo, por ejemplo 'analisis_inscritos_2006_2025.csv'
        nombre_archivo = f"{nombre_archivo}{extension}"

    # Finalmente, construimos la ruta completa combinando el directorio base y el nombre del archivo, y la devolvemos
    # Ej: outputs/tablas/analisis_inscritos_2006_2025.csv
    return directorio_base / nombre_archivo


def listar_directorios_base() -> dict[str, Path]:
    """
    Devuelve un diccionario con los directorios principales del proyecto.
    Útil para depuración o para otros módulos de configuración.
    """

    return {
        "raiz_proyecto": RAIZ_PROYECTO,
        "src": DIR_SRC,
        "data": DIR_DATA,
        "data_raw": DIR_DATA_RAW,
        "data_interim": DIR_DATA_INTERIM,
        "data_processed": DIR_DATA_PROCESSED,
        "outputs": DIR_OUTPUTS,
        "outputs_tablas": DIR_OUTPUTS_TABLAS,
        "outputs_graficos": DIR_OUTPUTS_GRAFICOS,
        "outputs_reportes": DIR_OUTPUTS_REPORTES,
        "outputs_modelos": DIR_OUTPUTS_MODELOS,
        "notebooks": DIR_NOTEBOOKS,
        "tests": DIR_TESTS,
    }


# Si ejecutamos este módulo directamente, se asegurarán los directorios y se imprimirán las rutas de los directorios base para verificar que todo esté configurado correctamente.
# Ej: python src/base/rutas.py
# Recordatorio para cualquiera que lea: Python le asigna el valor "__main__" a la variable __name__ cuando se ejecuta un módulo directamente, lo que permite que este bloque de código se ejecute solo en ese caso y no cuando el módulo es importado desde otro lugar.
if __name__ == "__main__":
    # Llamamos a la función para crear los directorios necesarios si no existen
    asegurar_directorios()

    # Luego iteramos sobre el diccionario de directorios base y los imprimimos para verificar que las rutas sean correctas (el metodo .items() devuelve una lista de tuplas con el nombre y la ruta de cada directorio)
    for nombre, ruta in listar_directorios_base().items():
        print(f"{nombre}: {ruta}")
