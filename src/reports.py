# Importamos la función de anotaciones futuras para permitir el uso de
# tipos de datos más avanzados y evitar problemas de importación circular en Python 3.7+.
from __future__ import annotations

# Importamos Path para manejar rutas de salida y pandas
# para exportar tablas tabulares a distintos formatos.
from pathlib import Path

import pandas as pd


# ==========================================================
# Utilidades internas de exportación
# ==========================================================

# Función para asegurar que el directorio de salida exista antes de exportar archivos.
def _asegurar_directorio(ruta: str | Path) -> Path:
    """
    Asegura que el directorio padre de una ruta exista y devuelve la ruta como Path.
    """
    ruta_path = Path(ruta)
    ruta_path.parent.mkdir(parents=True, exist_ok=True)
    return ruta_path


# ==========================================================
# Exportación de tablas
# ==========================================================

# Función para exportar un DataFrame a CSV.
def exportar_tabla_csv(
    tabla: pd.DataFrame,
    ruta_salida: str | Path,
    incluir_indice: bool = False,
) -> Path:
    """
    Exporta una tabla a formato CSV.

    Parámetros
    ----------
    tabla : pd.DataFrame
        Tabla a exportar.
    ruta_salida : str | Path
        Ruta completa del archivo de salida.
    incluir_indice : bool
        Si es True, exporta también el índice.

    Devuelve
    --------
    Path
        Ruta final del archivo exportado.
    """
    ruta = _asegurar_directorio(ruta_salida)
    tabla.to_csv(ruta, index=incluir_indice)
    return ruta


# Función para exportar un conjunto de tablas a un archivo Excel,
# utilizando una hoja por cada tabla.
def exportar_tablas_excel(
    tablas: dict[str, pd.DataFrame],
    ruta_salida: str | Path,
    incluir_indice: bool = False,
) -> Path:
    """
    Exporta múltiples tablas a un archivo Excel con varias hojas.

    Parámetros
    ----------
    tablas : dict[str, pd.DataFrame]
        Diccionario donde la clave será el nombre de la hoja
        y el valor será la tabla a exportar.
    ruta_salida : str | Path
        Ruta completa del archivo Excel.
    incluir_indice : bool
        Si es True, exporta también el índice en cada hoja.

    Devuelve
    --------
    Path
        Ruta final del archivo exportado.
    """
    ruta = _asegurar_directorio(ruta_salida)

    with pd.ExcelWriter(ruta, engine="openpyxl") as writer:
        for nombre_hoja, tabla in tablas.items():
            nombre_hoja_limpio = str(nombre_hoja)[:31]
            tabla.to_excel(writer, sheet_name=nombre_hoja_limpio, index=incluir_indice)

    return ruta


# ==========================================================
# Exportación de reportes de texto
# ==========================================================

# Función para escribir un reporte en texto plano.
def escribir_reporte_txt(
    contenido: str,
    ruta_salida: str | Path,
    encoding: str = "utf-8",
) -> Path:
    """
    Escribe un reporte de texto plano en disco.

    Parámetros
    ----------
    contenido : str
        Contenido textual del reporte.
    ruta_salida : str | Path
        Ruta completa del archivo de salida.
    encoding : str
        Codificación del archivo.

    Devuelve
    --------
    Path
        Ruta final del archivo generado.
    """
    ruta = _asegurar_directorio(ruta_salida)

    with open(ruta, "w", encoding=encoding) as archivo:
        archivo.write(contenido)

    return ruta


# Función para escribir un reporte en formato Markdown.
def escribir_reporte_markdown(
    contenido: str,
    ruta_salida: str | Path,
    encoding: str = "utf-8",
) -> Path:
    """
    Escribe un reporte en formato Markdown.

    Parámetros
    ----------
    contenido : str
        Contenido del reporte en Markdown.
    ruta_salida : str | Path
        Ruta completa del archivo de salida.
    encoding : str
        Codificación del archivo.

    Devuelve
    --------
    Path
        Ruta final del archivo generado.
    """
    ruta = _asegurar_directorio(ruta_salida)

    with open(ruta, "w", encoding=encoding) as archivo:
        archivo.write(contenido)

    return ruta


# ==========================================================
# Reportes simples a partir de tablas
# ==========================================================

# Función para construir un bloque Markdown simple a partir de una tabla.
def tabla_a_markdown(
    tabla: pd.DataFrame,
    titulo: str | None = None,
    incluir_indice: bool = False,
) -> str:
    """
    Convierte una tabla en un bloque Markdown.

    Parámetros
    ----------
    tabla : pd.DataFrame
        Tabla a convertir.
    titulo : str | None
        Título opcional del bloque.
    incluir_indice : bool
        Si es True, incluye el índice en la conversión.

    Devuelve
    --------
    str
        Tabla representada en formato Markdown.
    """
    partes: list[str] = []

    if titulo:
        partes.append(f"## {titulo}\n")

    partes.append(tabla.to_markdown(index=incluir_indice))
    partes.append("")

    return "\n".join(partes)


# Función para construir un reporte Markdown a partir de varias tablas.
def construir_reporte_markdown(
    secciones: dict[str, pd.DataFrame],
    titulo_general: str | None = None,
    incluir_indice: bool = False,
) -> str:
    """
    Construye un reporte Markdown a partir de varias tablas.

    Parámetros
    ----------
    secciones : dict[str, pd.DataFrame]
        Diccionario donde cada clave es el título de la sección
        y cada valor es la tabla correspondiente.
    titulo_general : str | None
        Título principal del reporte.
    incluir_indice : bool
        Si es True, incluye el índice de las tablas.

    Devuelve
    --------
    str
        Contenido completo del reporte en Markdown.
    """
    partes: list[str] = []

    if titulo_general:
        partes.append(f"# {titulo_general}\n")

    for titulo_seccion, tabla in secciones.items():
        partes.append(
            tabla_a_markdown(
                tabla=tabla,
                titulo=titulo_seccion,
                incluir_indice=incluir_indice,
            )
        )

    return "\n".join(partes)