from pathlib import Path

# Resolvemos la ruta desde este archivo de config.py
# Y luego con .parent.parent subimos dos niveles 
# para llegar a la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Definimos las rutas para los datos y salidas
RAW_DATA_DIR = BASE_DIR / "data" / "raw" # Aquí se almacenan los datos sin procesar
CLEAN_DATA_DIR = BASE_DIR / "data" / "clean" # Aquí se almacenan los datos limpios después del procesamiento
OUTPUTS_DIR = BASE_DIR / "outputs" # Aquí se almacenan los resultados, gráficos y reportes generados por el proyecto
GRAFICOS_DIR = OUTPUTS_DIR / "graficos" # Aquí se almacenan los gráficos generados por el proyecto
REPORTES_DIR = OUTPUTS_DIR / "reportes" # Aquí se almacenan los reportes generados por el proyecto

# Definimos las rutas para los datasets específicos
RAW_FILE = RAW_DATA_DIR / "dataset.csv" # Archivo original sin procesar
CLEAN_FILE = CLEAN_DATA_DIR / "dataset_clean.csv" # Archivo limpio después del procesamiento