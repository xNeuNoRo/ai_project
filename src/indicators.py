# Importamos la función de anotaciones futuras para permitir el uso de
# tipos de datos más avanzados y evitar problemas de importación circular en Python 3.7+.
from __future__ import annotations

# Importamos pandas para construir tablas e indicadores derivados
# a partir de datasets tabulares.
import pandas as pd

from src.analysis import comparar_periodos


# ==========================================================
# Funciones auxiliares internas
# ==========================================================

# Función para asegurar que una entrada de columnas se convierta en lista,
# permitiendo trabajar de forma consistente tanto con una columna como con varias.
def _asegurar_lista_columnas(columnas: str | list[str] | None) -> list[str]:
    """
    Devuelve una lista de columnas a partir de un string, una lista o None.
    """
    if columnas is None:
        return []

    if isinstance(columnas, str):
        return [columnas]

    return columnas


# Función auxiliar para resumir los huecos temporales de una serie numérica.
def _resumir_huecos_periodos(
    serie_periodos: pd.Series,
    columna_periodo: str,
) -> dict[str, object]:
    """
    Resume los huecos temporales existentes en una serie de periodos.
    """
    periodos_observados = sorted(serie_periodos.dropna().astype(int).unique().tolist())

    if not periodos_observados:
        return {
            "columna_periodo": columna_periodo,
            "periodo_minimo": None,
            "periodo_maximo": None,
            "periodos_esperados": 0,
            "periodos_observados": 0,
            "periodos_faltantes": [],
            "cantidad_huecos": 0,
        }

    periodo_minimo = min(periodos_observados)
    periodo_maximo = max(periodos_observados)

    periodos_esperados_lista = list(range(periodo_minimo, periodo_maximo + 1))
    periodos_faltantes = [
        periodo
        for periodo in periodos_esperados_lista
        if periodo not in periodos_observados
    ]

    return {
        "columna_periodo": columna_periodo,
        "periodo_minimo": periodo_minimo,
        "periodo_maximo": periodo_maximo,
        "periodos_esperados": len(periodos_esperados_lista),
        "periodos_observados": len(periodos_observados),
        "periodos_faltantes": periodos_faltantes,
        "cantidad_huecos": len(periodos_faltantes),
    }


# ==========================================================
# Crecimiento temporal
# ==========================================================

# Función para calcular crecimiento absoluto y porcentual por periodo,
# opcionalmente segmentado por uno o varios grupos.
def calcular_crecimiento(
    df: pd.DataFrame,
    columna_periodo: str,
    columna_valor: str,
    columnas_grupo: str | list[str] | None = None,
    agregacion: str = "sum",
    incluir_nulos: bool = False,
) -> pd.DataFrame:
    """
    Calcula crecimiento absoluto y porcentual por periodo.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame de entrada.
    columna_periodo : str
        Columna temporal o de periodo.
    columna_valor : str
        Columna numérica sobre la cual se calcula el crecimiento.
    columnas_grupo : str | list[str] | None
        Columna o columnas opcionales para segmentar el crecimiento.
    agregacion : str
        Función de agregación aplicada antes de calcular el crecimiento.
    incluir_nulos : bool
        Si es True, incluye grupos con valores nulos.

    Devuelve
    --------
    pd.DataFrame
        Tabla con valor agregado, cambio absoluto y cambio porcentual.
    """
    columnas_grupo_lista = _asegurar_lista_columnas(columnas_grupo)
    columnas_agrupacion = columnas_grupo_lista + [columna_periodo]

    resultado = (
        df.groupby(columnas_agrupacion, dropna=not incluir_nulos)[columna_valor]
        .agg(agregacion)
        .reset_index(name="valor")
    )

    columnas_orden = columnas_grupo_lista + [columna_periodo]
    resultado = resultado.sort_values(by=columnas_orden).reset_index(drop=True)

    if columnas_grupo_lista:
        resultado["cambio_absoluto"] = resultado.groupby(columnas_grupo_lista)["valor"].diff()
        resultado["cambio_porcentual"] = (
            resultado.groupby(columnas_grupo_lista)["valor"].pct_change()
        ) * 100
    else:
        resultado["cambio_absoluto"] = resultado["valor"].diff()
        resultado["cambio_porcentual"] = resultado["valor"].pct_change() * 100

    return resultado


# ==========================================================
# Participación porcentual
# ==========================================================

# Función para calcular la participación porcentual de cada grupo
# dentro de un total definido por una o varias columnas.
def calcular_participacion(
    df: pd.DataFrame,
    columnas_grupo: str | list[str],
    columna_valor: str,
    dentro_de: str | list[str],
    agregacion: str = "sum",
    incluir_nulos: bool = False,
) -> pd.DataFrame:
    """
    Calcula la participación porcentual de cada grupo dentro de un total.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame de entrada.
    columnas_grupo : str | list[str]
        Columnas por las que se agrupa el resultado final.
    columna_valor : str
        Columna numérica a agregar.
    dentro_de : str | list[str]
        Columna o columnas dentro de las que se calcula el total.
        Deben estar incluidas dentro de columnas_grupo.
    agregacion : str
        Función de agregación aplicada sobre la columna de valor.
    incluir_nulos : bool
        Si es True, incluye grupos con valores nulos.

    Devuelve
    --------
    pd.DataFrame
        Tabla con valor agregado, total y participación porcentual.
    """
    columnas_grupo_lista = _asegurar_lista_columnas(columnas_grupo)
    columnas_total_lista = _asegurar_lista_columnas(dentro_de)

    columnas_faltantes = [
        columna
        for columna in columnas_total_lista
        if columna not in columnas_grupo_lista
    ]

    if columnas_faltantes:
        raise ValueError(
            "Las columnas de 'dentro_de' deben estar incluidas en 'columnas_grupo'."
        )

    resultado = (
        df.groupby(columnas_grupo_lista, dropna=not incluir_nulos)[columna_valor]
        .agg(agregacion)
        .reset_index(name="valor")
    )

    resultado["total_dentro_de"] = (
        resultado.groupby(columnas_total_lista)["valor"].transform("sum")
    )

    resultado["participacion_porcentual"] = (
        resultado["valor"] / resultado["total_dentro_de"].replace(0, pd.NA)
    ) * 100

    return resultado


# ==========================================================
# Ranking de cambios
# ==========================================================

# Función para construir un ranking de cambios entre dos periodos,
# reutilizando la lógica de comparación entre periodos.
def ranking_cambios(
    df: pd.DataFrame,
    columna_periodo: str,
    columna_grupo: str,
    columna_valor: str,
    periodo_inicial: object,
    periodo_final: object,
    agregacion: str = "sum",
    criterio_orden: str = "cambio_absoluto",
    ascendente: bool = False,
    top_n: int | None = None,
) -> pd.DataFrame:
    """
    Construye un ranking de cambios entre dos periodos.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame de entrada.
    columna_periodo : str
        Columna temporal o de periodo.
    columna_grupo : str
        Columna que define los grupos a comparar.
    columna_valor : str
        Columna numérica a agregar.
    periodo_inicial : object
        Periodo inicial de comparación.
    periodo_final : object
        Periodo final de comparación.
    agregacion : str
        Función de agregación aplicada sobre la columna de valor.
    criterio_orden : str
        Columna por la cual ordenar el ranking.
        Ejemplos: "cambio_absoluto", "cambio_porcentual", "valor_final".
    ascendente : bool
        Define si el orden es ascendente o descendente.
    top_n : int | None
        Si se indica, devuelve solo las primeras N filas.

    Devuelve
    --------
    pd.DataFrame
        Tabla ordenada según el criterio de cambio.
    """
    resultado = comparar_periodos(
        df=df,
        columna_periodo=columna_periodo,
        columna_grupo=columna_grupo,
        columna_valor=columna_valor,
        periodo_inicial=periodo_inicial,
        periodo_final=periodo_final,
        agregacion=agregacion,
    )

    tabla = resultado["tabla"].sort_values(
        by=criterio_orden,
        ascending=ascendente,
    ).reset_index(drop=True)

    if top_n is not None:
        tabla = tabla.head(top_n).reset_index(drop=True)

    return tabla


# ==========================================================
# Detección de huecos temporales
# ==========================================================

# Función para detectar periodos faltantes en una serie temporal,
# opcionalmente segmentada por uno o varios grupos.
def detectar_huecos_temporales(
    df: pd.DataFrame,
    columna_periodo: str,
    columnas_grupo: str | list[str] | None = None,
) -> pd.DataFrame:
    """
    Detecta huecos temporales en una columna de periodo.

    La columna de periodo debe ser numérica o convertible a entero,
    como ocurre típicamente con columnas de año.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame de entrada.
    columna_periodo : str
        Columna temporal o de periodo.
    columnas_grupo : str | list[str] | None
        Columna o columnas opcionales para detectar huecos por grupo.

    Devuelve
    --------
    pd.DataFrame
        Tabla con periodos faltantes y cantidad de huecos detectados.
    """
    columnas_grupo_lista = _asegurar_lista_columnas(columnas_grupo)

    serie_original = df[columna_periodo]
    serie_convertida = pd.to_numeric(serie_original, errors="coerce")

    mascara_no_convertible = serie_original.notna() & serie_convertida.isna()
    if mascara_no_convertible.any():
        raise ValueError(
            "La columna de periodo debe ser numérica o convertible a valores enteros."
        )

    df_trabajo = df.copy()
    df_trabajo[columna_periodo] = serie_convertida

    if not columnas_grupo_lista:
        resumen = _resumir_huecos_periodos(
            df_trabajo[columna_periodo],
            columna_periodo=columna_periodo,
        )
        return pd.DataFrame([resumen])

    filas_resultado: list[dict[str, object]] = []

    for claves_grupo, grupo_df in df_trabajo.groupby(columnas_grupo_lista, dropna=False):
        if not isinstance(claves_grupo, tuple):
            claves_grupo = (claves_grupo,)

        fila_base = {
            nombre_columna: valor_columna
            for nombre_columna, valor_columna in zip(columnas_grupo_lista, claves_grupo)
        }

        resumen = _resumir_huecos_periodos(
            grupo_df[columna_periodo],
            columna_periodo=columna_periodo,
        )

        fila_base.update(resumen)
        filas_resultado.append(fila_base)

    return pd.DataFrame(filas_resultado)


# ==========================================================
# Indicadores descriptivos derivados
# ==========================================================

# Función para construir una tabla de indicadores descriptivos
# agrupados por una o varias columnas.
def construir_tabla_indicadores(
    df: pd.DataFrame,
    columnas_grupo: str | list[str],
    columna_valor: str,
    incluir_nulos: bool = False,
) -> pd.DataFrame:
    """
    Construye una tabla de indicadores descriptivos por grupo.

    Incluye:
    - total
    - promedio
    - mediana
    - mínimo
    - máximo
    - desviación estándar
    - cantidad de registros

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame de entrada.
    columnas_grupo : str | list[str]
        Columna o columnas por las que se agrupa.
    columna_valor : str
        Columna numérica sobre la cual se construyen los indicadores.
    incluir_nulos : bool
        Si es True, incluye grupos con valores nulos.

    Devuelve
    --------
    pd.DataFrame
        Tabla con indicadores descriptivos por grupo.
    """
    columnas_grupo_lista = _asegurar_lista_columnas(columnas_grupo)

    resultado = (
        df.groupby(columnas_grupo_lista, dropna=not incluir_nulos)[columna_valor]
        .agg(
            total="sum",
            promedio="mean",
            mediana="median",
            minimo="min",
            maximo="max",
            desviacion_estandar="std",
            registros="count",
        )
        .reset_index()
    )

    return resultado