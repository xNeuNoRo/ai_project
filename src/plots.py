# Importamos la función de anotaciones futuras para permitir el uso de
# tipos de datos más avanzados y evitar problemas de importación circular en Python 3.7+.
from __future__ import annotations

# Importamos Path para guardar figuras y matplotlib/pandas
# para construir gráficos reutilizables.
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# ==========================================================
# Utilidades base de gráficos
# ==========================================================

# Función para guardar una figura en disco, creando carpetas si hace falta.
def guardar_figura(
    fig: plt.Figure,
    ruta_salida: str | Path,
    dpi: int = 300,
    ajustar: bool = True,
) -> Path:
    """
    Guarda una figura en disco y devuelve la ruta final.

    Parámetros
    ----------
    fig : plt.Figure
        Figura de matplotlib.
    ruta_salida : str | Path
        Ruta completa de salida.
    dpi : int
        Resolución de guardado.
    ajustar : bool
        Si es True, aplica tight_layout() antes de guardar.

    Devuelve
    --------
    Path
        Ruta final donde se guardó la figura.
    """
    ruta = Path(ruta_salida)

    if ajustar:
        fig.tight_layout()

    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta, dpi=dpi, bbox_inches="tight")

    return ruta


# ==========================================================
# Serie temporal
# ==========================================================

# Función para graficar una serie temporal simple,
# opcionalmente segmentada por grupo.
def graficar_serie_temporal(
    df: pd.DataFrame,
    columna_x: str,
    columna_y: str,
    columna_grupo: str | None = None,
    titulo: str | None = None,
    etiqueta_x: str | None = None,
    etiqueta_y: str | None = None,
    rotacion_x: int = 45,
    mostrar_leyenda: bool = True,
    tamano_figura: tuple[int, int] = (10, 6),
) -> tuple[plt.Figure, plt.Axes]:
    """
    Grafica una serie temporal simple o segmentada por grupo.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame de entrada ya resumido.
    columna_x : str
        Columna para el eje X.
    columna_y : str
        Columna para el eje Y.
    columna_grupo : str | None
        Columna opcional para separar múltiples líneas.
    titulo : str | None
        Título del gráfico.
    etiqueta_x : str | None
        Etiqueta del eje X.
    etiqueta_y : str | None
        Etiqueta del eje Y.
    rotacion_x : int
        Rotación de etiquetas del eje X.
    mostrar_leyenda : bool
        Si es True, muestra la leyenda cuando hay grupos.
    tamano_figura : tuple[int, int]
        Tamaño de la figura.

    Devuelve
    --------
    tuple[plt.Figure, plt.Axes]
        Figura y ejes del gráfico.
    """
    fig, ax = plt.subplots(figsize=tamano_figura)

    if columna_grupo:
        for nombre_grupo, grupo_df in df.groupby(columna_grupo):
            grupo_ordenado = grupo_df.sort_values(by=columna_x)
            ax.plot(
                grupo_ordenado[columna_x],
                grupo_ordenado[columna_y],
                marker="o",
                label=str(nombre_grupo),
            )
    else:
        df_ordenado = df.sort_values(by=columna_x)
        ax.plot(
            df_ordenado[columna_x],
            df_ordenado[columna_y],
            marker="o",
        )

    ax.set_title(titulo or "Serie temporal")
    ax.set_xlabel(etiqueta_x or columna_x)
    ax.set_ylabel(etiqueta_y or columna_y)
    ax.tick_params(axis="x", rotation=rotacion_x)
    ax.grid(True, alpha=0.3)

    if columna_grupo and mostrar_leyenda:
        ax.legend()

    return fig, ax


# ==========================================================
# Barras
# ==========================================================

# Función para graficar barras simples a partir de una tabla resumida.
def graficar_barras(
    df: pd.DataFrame,
    columna_x: str,
    columna_y: str,
    titulo: str | None = None,
    etiqueta_x: str | None = None,
    etiqueta_y: str | None = None,
    rotacion_x: int = 45,
    tamano_figura: tuple[int, int] = (10, 6),
) -> tuple[plt.Figure, plt.Axes]:
    """
    Grafica un diagrama de barras simple.
    """
    fig, ax = plt.subplots(figsize=tamano_figura)

    ax.bar(df[columna_x].astype(str), df[columna_y])

    ax.set_title(titulo or "Gráfico de barras")
    ax.set_xlabel(etiqueta_x or columna_x)
    ax.set_ylabel(etiqueta_y or columna_y)
    ax.tick_params(axis="x", rotation=rotacion_x)

    return fig, ax


# Función para graficar el top N de una tabla resumida.
def graficar_barras_top_n(
    df: pd.DataFrame,
    columna_categoria: str,
    columna_valor: str,
    top_n: int = 10,
    ascendente: bool = False,
    titulo: str | None = None,
    etiqueta_x: str | None = None,
    etiqueta_y: str | None = None,
    rotacion_x: int = 45,
    tamano_figura: tuple[int, int] = (10, 6),
) -> tuple[plt.Figure, plt.Axes]:
    """
    Grafica barras para las primeras N categorías según una columna de valor.
    """
    df_top = (
        df.sort_values(by=columna_valor, ascending=ascendente)
        .head(top_n)
        .reset_index(drop=True)
    )

    fig, ax = plt.subplots(figsize=tamano_figura)

    ax.bar(df_top[columna_categoria].astype(str), df_top[columna_valor])

    ax.set_title(titulo or f"Top {top_n}")
    ax.set_xlabel(etiqueta_x or columna_categoria)
    ax.set_ylabel(etiqueta_y or columna_valor)
    ax.tick_params(axis="x", rotation=rotacion_x)

    return fig, ax


# ==========================================================
# Barras apiladas
# ==========================================================

# Función para graficar barras apiladas a partir de una tabla pivote.
def graficar_barras_apiladas(
    df: pd.DataFrame,
    columna_x: str,
    columnas_valor: list[str],
    titulo: str | None = None,
    etiqueta_x: str | None = None,
    etiqueta_y: str | None = None,
    rotacion_x: int = 45,
    mostrar_leyenda: bool = True,
    tamano_figura: tuple[int, int] = (11, 6),
) -> tuple[plt.Figure, plt.Axes]:
    """
    Grafica barras apiladas a partir de una tabla ya pivotada.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame en formato ancho.
    columna_x : str
        Columna base del eje X.
    columnas_valor : list[str]
        Columnas numéricas a apilar.
    """
    fig, ax = plt.subplots(figsize=tamano_figura)

    base = pd.Series([0] * len(df), index=df.index, dtype="float64")

    for nombre_columna in columnas_valor:
        ax.bar(
            df[columna_x].astype(str),
            df[nombre_columna],
            bottom=base,
            label=str(nombre_columna),
        )
        base = base + df[nombre_columna].fillna(0)

    ax.set_title(titulo or "Barras apiladas")
    ax.set_xlabel(etiqueta_x or columna_x)
    ax.set_ylabel(etiqueta_y or "valor")
    ax.tick_params(axis="x", rotation=rotacion_x)

    if mostrar_leyenda:
        ax.legend()

    return fig, ax


# ==========================================================
# Heatmap
# ==========================================================

# Función para graficar un heatmap a partir de una tabla pivote.
def graficar_heatmap(
    tabla_pivote: pd.DataFrame,
    columna_indice: str,
    titulo: str | None = None,
    etiqueta_x: str | None = None,
    etiqueta_y: str | None = None,
    tamano_figura: tuple[int, int] = (12, 6),
) -> tuple[plt.Figure, plt.Axes]:
    """
    Grafica un heatmap a partir de una tabla pivote.

    Parámetros
    ----------
    tabla_pivote : pd.DataFrame
        Tabla pivote en formato ancho.
    columna_indice : str
        Columna que identifica las filas.
    titulo : str | None
        Título del gráfico.
    etiqueta_x : str | None
        Etiqueta del eje X.
    etiqueta_y : str | None
        Etiqueta del eje Y.

    Devuelve
    --------
    tuple[plt.Figure, plt.Axes]
        Figura y ejes del gráfico.
    """
    datos = tabla_pivote.set_index(columna_indice)
    matriz = datos.to_numpy()

    fig, ax = plt.subplots(figsize=tamano_figura)

    imagen = ax.imshow(matriz, aspect="auto")

    ax.set_title(titulo or "Heatmap")
    ax.set_xlabel(etiqueta_x or "columnas")
    ax.set_ylabel(etiqueta_y or columna_indice)

    ax.set_xticks(range(len(datos.columns)))
    ax.set_xticklabels([str(col) for col in datos.columns], rotation=45, ha="right")

    ax.set_yticks(range(len(datos.index)))
    ax.set_yticklabels([str(idx) for idx in datos.index])

    fig.colorbar(imagen, ax=ax)

    return fig, ax