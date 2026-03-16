# Importamos la función de anotaciones futuras para permitir el uso de
# tipos de datos más avanzados y evitar problemas de importación circular en Python 3.7+.
from __future__ import annotations

# Importamos Path para manejar rutas y pandas para cargar y guardar tablas.
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import obtener_ruta_datos


# Codificaciones comunes para probar al cargar archivos CSV.
CODIFICACIONES_CSV = ("utf-8", "utf-8-sig", "latin1", "cp1252")

# Reemplazos simples para corregir caracteres raros frecuentes.
REEMPLAZOS_TEXTO = {
    "ÿ": " ",
    "¢": "ó",
    "¤": "ñ",
    "¡": "í",
    "\x82": "é",
    "\xa0": "á",
}


# ==========================================================
# Carga de archivos
# ==========================================================

# Función para cargar un CSV probando varias codificaciones.
def cargar_csv(ruta_csv: str | Path, **kwargs: Any) -> pd.DataFrame:
    """
    Carga un archivo CSV probando varias codificaciones comunes.
    """
    ultimo_error = None

    for codificacion in CODIFICACIONES_CSV:
        try:
            return pd.read_csv(ruta_csv, encoding=codificacion, **kwargs)
        except UnicodeDecodeError as error:
            ultimo_error = error

    if ultimo_error is not None:
        raise ultimo_error

    raise ValueError("No fue posible cargar el archivo CSV.")


# Función general para cargar una tabla según su extensión.
def cargar_tabla(ruta: str | Path, **kwargs: Any) -> pd.DataFrame:
    """
    Carga una tabla desde CSV o Excel según la extensión del archivo.
    """
    ruta = Path(ruta)
    extension = ruta.suffix.lower()

    if extension == ".csv":
        return cargar_csv(ruta, **kwargs)

    if extension in {".xlsx", ".xls"}:
        return pd.read_excel(ruta, **kwargs)

    raise ValueError(f"Formato no soportado: {extension}")


# Función para cargar un dataset del proyecto por nombre lógico.
def cargar_dataset(
    nombre_dataset: str,
    etapa: str = "raw",
    extension: str = "csv",
    **kwargs: Any,
) -> pd.DataFrame:
    """
    Carga un dataset del proyecto según su nombre, etapa y extensión.
    """
    ruta = obtener_ruta_datos(
        nombre_dataset=nombre_dataset,
        etapa=etapa,
        extension=extension,
    )
    return cargar_tabla(ruta, **kwargs)


# ==========================================================
# Limpieza básica
# ==========================================================

# Función para limpiar un valor de texto.
def limpiar_texto(valor: object) -> object:
    """
    Limpia caracteres raros y espacios innecesarios en un valor de texto.
    """
    if not isinstance(valor, str):
        return valor

    texto = valor

    for origen, destino in REEMPLAZOS_TEXTO.items():
        texto = texto.replace(origen, destino)

    texto = " ".join(texto.split())

    return texto.strip()


# Función para limpiar columnas de texto de un DataFrame.
def limpiar_columnas_texto(
    df: pd.DataFrame,
    columnas: list[str] | None = None,
) -> pd.DataFrame:
    """
    Limpia columnas de texto aplicando reemplazos básicos y normalización de espacios.
    """
    df_limpio = df.copy()

    if columnas is None:
        columnas = df_limpio.select_dtypes(include=["object", "string"]).columns.tolist()

    for columna in columnas:
        if columna in df_limpio.columns:
            df_limpio[columna] = df_limpio[columna].map(limpiar_texto)

    return df_limpio


# Función para preparar un dataset con limpieza básica.
def preparar_dataset(
    df: pd.DataFrame,
    columnas_texto: list[str] | None = None,
    eliminar_duplicados: bool = True,
) -> pd.DataFrame:
    """
    Aplica limpieza básica al dataset:
    - limpia texto
    - elimina duplicados si se indica
    """
    df_limpio = limpiar_columnas_texto(df, columnas=columnas_texto)

    if eliminar_duplicados:
        df_limpio = df_limpio.drop_duplicates().reset_index(drop=True)

    return df_limpio


# Función de conveniencia para cargar y preparar en un solo paso.
def cargar_y_preparar_dataset(
    nombre_dataset: str,
    etapa: str = "raw",
    extension: str = "csv",
    columnas_texto: list[str] | None = None,
    eliminar_duplicados: bool = True,
    **kwargs: Any,
) -> pd.DataFrame:
    """
    Carga un dataset y aplica una limpieza básica en un solo paso.
    """
    df = cargar_dataset(
        nombre_dataset=nombre_dataset,
        etapa=etapa,
        extension=extension,
        **kwargs,
    )

    return preparar_dataset(
        df,
        columnas_texto=columnas_texto,
        eliminar_duplicados=eliminar_duplicados,
    )


# ==========================================================
# Guardado de archivos
# ==========================================================

# Función para guardar una tabla en CSV o Excel.
def guardar_tabla(
    tabla: pd.DataFrame,
    ruta_salida: str | Path,
    incluir_indice: bool = False,
    **kwargs: Any,
) -> Path:
    """
    Guarda una tabla según la extensión del archivo.
    """
    ruta = Path(ruta_salida)
    ruta.parent.mkdir(parents=True, exist_ok=True)

    extension = ruta.suffix.lower()

    if extension == ".csv":
        tabla.to_csv(ruta, index=incluir_indice, **kwargs)
        return ruta

    if extension in {".xlsx", ".xls"}:
        tabla.to_excel(ruta, index=incluir_indice, **kwargs)
        return ruta

    raise ValueError(f"Formato no soportado: {extension}")


# Función para guardar un dataset del proyecto.
def guardar_dataset(
    df: pd.DataFrame,
    nombre_dataset: str,
    etapa: str = "processed",
    extension: str = "csv",
    incluir_indice: bool = False,
    **kwargs: Any,
) -> Path:
    """
    Guarda un dataset del proyecto según su nombre, etapa y extensión.
    """
    ruta = obtener_ruta_datos(
        nombre_dataset=nombre_dataset,
        etapa=etapa,
        extension=extension,
    )

    return guardar_tabla(
        tabla=df,
        ruta_salida=ruta,
        incluir_indice=incluir_indice,
        **kwargs,
    )