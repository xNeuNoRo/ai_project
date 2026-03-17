from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys


# ==========================================================
# Configuración general
# ==========================================================

REPO_URL = "https://github.com/xNeuNoRo/ai_project.git"
REPO_BRANCH = "refactor/structure"
REPO_DIR = Path("/content/ai_project")

# Carpeta base en Google Drive para datos y salidas
DRIVE_BASE = Path("/content/drive/MyDrive/ai_project_data")
RAW_DIR = DRIVE_BASE / "raw"
PROCESSED_DIR = DRIVE_BASE / "processed"
OUTPUTS_DIR = DRIVE_BASE / "outputs"

# Esta variable de entorno le indica al sistema de rutas del proyecto
# que use Google Drive como base para data y outputs en Colab.
os.environ["AI_PROJECT_STORAGE_DIR"] = str(DRIVE_BASE)

# Dependencias mínimas necesarias para el proyecto
PAQUETES_BASE = [
    "pandas",
    "matplotlib",
    "openpyxl",
    "tabulate",
    "scikit-learn",
]


# ==========================================================
# Utilidades
# ==========================================================

def ejecutar_comando(comando: list[str]) -> None:
    """
    Ejecuta un comando del sistema y falla si el comando falla.
    """
    subprocess.run(comando, check=True)


def instalar_paquetes(paquetes: list[str]) -> None:
    """
    Instala paquetes con pip.
    """
    if not paquetes:
        return

    ejecutar_comando([sys.executable, "-m", "pip", "install", "-q", *paquetes])


def clonar_o_actualizar_repo() -> None:
    """
    Clona el repositorio si no existe. Si ya existe, lo actualiza.
    """
    if not REPO_DIR.exists():
        ejecutar_comando([
            "git",
            "clone",
            "-b",
            REPO_BRANCH,
            REPO_URL,
            str(REPO_DIR),
        ])
    else:
        ejecutar_comando(["git", "-C", str(REPO_DIR), "fetch", "origin"])
        ejecutar_comando(["git", "-C", str(REPO_DIR), "checkout", REPO_BRANCH])
        ejecutar_comando(["git", "-C", str(REPO_DIR), "pull", "origin", REPO_BRANCH])


def agregar_repo_al_path() -> None:
    """
    Agrega la raíz del repo y src al sys.path para poder importar módulos.
    """
    rutas_a_agregar = [
        str(REPO_DIR),
        str(REPO_DIR / "src"),
    ]

    for ruta in rutas_a_agregar:
        if ruta not in sys.path:
            sys.path.append(ruta)


def crear_directorios_drive() -> None:
    """
    Crea la estructura base de carpetas en Google Drive.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def copiar_dataset_si_no_existe(
    nombre_archivo: str,
    destino_subcarpeta: str = "raw",
) -> None:
    """
    Copia un dataset desde Drive al repo si aún no existe en data/raw.

    Esto es útil si quieres mantener los datos en Drive pero trabajar
    con la estructura del repo local dentro de Colab.
    """
    origen = DRIVE_BASE / destino_subcarpeta / nombre_archivo
    destino = REPO_DIR / "data" / destino_subcarpeta / nombre_archivo

    if origen.exists() and not destino.exists():
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(origen.read_bytes())


def verificar_imports() -> None:
    """
    Verifica que los módulos principales del proyecto importen correctamente.
    """
    from src.io import cargar_y_preparar_dataset, guardar_dataset
    from src.validation import validar_esquema
    from src.profiling import perfilar_dataset
    from src.analysis import resumir_por_grupo
    from src.indicators import calcular_crecimiento
    from src.plots import graficar_serie_temporal
    from src.reports import exportar_tabla_csv

    _ = (
        cargar_y_preparar_dataset,
        guardar_dataset,
        validar_esquema,
        perfilar_dataset,
        resumir_por_grupo,
        calcular_crecimiento,
        graficar_serie_temporal,
        exportar_tabla_csv,
    )


# ==========================================================
# Setup principal
# ==========================================================

def setup_colab() -> None:
    """
    Prepara el entorno de Colab para trabajar con el proyecto.
    """
    from google.colab import drive

    print("Montando Google Drive...")
    drive.mount("/content/drive")

    print("Creando directorios base en Drive...")
    crear_directorios_drive()

    print("Clonando o actualizando repositorio...")
    clonar_o_actualizar_repo()

    print("Actualizando pip...")
    ejecutar_comando([sys.executable, "-m", "pip", "install", "-q", "--upgrade", "pip"])

    print("Instalando dependencias base...")
    instalar_paquetes(PAQUETES_BASE)

    print("Agregando repo al PYTHONPATH...")
    agregar_repo_al_path()

    print("Verificando imports principales...")
    verificar_imports()

    print("\nSetup completado correctamente.")
    print(f"Repo: {REPO_DIR}")
    print(f"Drive base: {DRIVE_BASE}")
    print(f"Raw dir: {RAW_DIR}")
    print(f"Processed dir: {PROCESSED_DIR}")
    print(f"Outputs dir: {OUTPUTS_DIR}")


# ==========================================================
# Ejecución directa
# ==========================================================

setup_colab()