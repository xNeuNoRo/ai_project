# Importamos la función de anotaciones futuras para permitir el uso de
# tipos de datos más avanzados y evitar problemas de importación circular en Python 3.7+.
from __future__ import annotations

# Importamos pandas y TypedDict para definir estructuras claras
# para los resultados de análisis tabular.
from typing import TypedDict

import pandas as pd


# Estructura de resultado para comparaciones entre periodos
class ResultadoComparacionPeriodos(TypedDict):
    tabla: pd.DataFrame
    periodo_inicial: object
    periodo_final: object
    columna_periodo: str
    columna_grupo: str
    columna_valor: str


# ==========================================================
# Funciones auxiliares de análisis
# ==========================================================

# Función para asegurar que una entrada de columnas se convierta en lista,
# permitiendo trabajar de forma consistente tanto con una columna como con varias.
def _asegurar_lista_columnas(columnas: str | list[str]) -> list[str]:
    """
    Devuelve una lista de columnas a partir de un string o una lista.
    """
    if isinstance(columnas, str):
        return [columnas]
    return columnas


# ==========================================================
# Análisis genérico por grupos
# ==========================================================

# Función genérica para resumir un DataFrame por una o varias columnas de agrupación.
def resumir_por_grupo(
    df: pd.DataFrame,
    columnas_grupo: str | list[str],
    columna_valor: str | None = None,
    agregacion: str = "count",
    incluir_nulos: bool = False,
    ordenar: bool = True,
    ascendente: bool = False,
) -> pd.DataFrame:
    """
    Resume un DataFrame por una o varias columnas de agrupación.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame de entrada.
    columnas_grupo : str | list[str]
        Columna o columnas por las que se agrupa.
    columna_valor : str | None
        Columna sobre la cual aplicar la agregación.
        Si no se indica, se cuenta la cantidad de registros.
    agregacion : str
        Función de agregación a aplicar.
        Ejemplos: "count", "sum", "mean", "median", "max", "min".
    incluir_nulos : bool
        Si es True, incluye grupos con valores nulos.
    ordenar : bool
        Si es True, ordena el resultado por la columna agregada.
    ascendente : bool
        Define si el orden es ascendente o descendente.

    Devuelve
    --------
    pd.DataFrame
        Tabla resumida por grupo.
    """
    columnas_grupo_lista = _asegurar_lista_columnas(columnas_grupo)

    if columna_valor is None:
        resultado = (
            df.groupby(columnas_grupo_lista, dropna=not incluir_nulos)
            .size()
            .reset_index(name="conteo")
        )
        columna_resultado = "conteo"
    else:
        resultado = (
            df.groupby(columnas_grupo_lista, dropna=not incluir_nulos)[
                columna_valor]
            .agg(agregacion)
            .reset_index(name=f"{agregacion}_{columna_valor}")
        )
        columna_resultado = f"{agregacion}_{columna_valor}"

    if ordenar:
        resultado = resultado.sort_values(
            by=columna_resultado,
            ascending=ascendente,
        ).reset_index(drop=True)

    return resultado


# Función para comparar grupos a partir de una columna de agrupación
# y una columna objetivo con una agregación configurable.
def comparar_grupos(
    df: pd.DataFrame,
    columna_grupo: str,
    columna_valor: str,
    agregacion: str = "mean",
    incluir_nulos: bool = False,
    ordenar: bool = True,
    ascendente: bool = False,
) -> pd.DataFrame:
    """
    Compara grupos aplicando una agregación sobre una columna objetivo.
    """
    return resumir_por_grupo(
        df=df,
        columnas_grupo=columna_grupo,
        columna_valor=columna_valor,
        agregacion=agregacion,
        incluir_nulos=incluir_nulos,
        ordenar=ordenar,
        ascendente=ascendente,
    )


# ==========================================================
# Análisis temporal básico
# ==========================================================

# Función para resumir una serie temporal por una columna de periodo,
# con posibilidad de agregar además por una columna secundaria.
def resumir_serie_temporal(
    df: pd.DataFrame,
    columna_periodo: str,
    columna_valor: str | None = None,
    agregacion: str = "count",
    columna_grupo: str | None = None,
    incluir_nulos: bool = False,
) -> pd.DataFrame:
    """
    Resume una serie temporal por periodo, opcionalmente segmentada por grupo.
    """
    columnas_agrupacion: list[str] = [columna_periodo]

    if columna_grupo:
        columnas_agrupacion.append(columna_grupo)

    resultado = resumir_por_grupo(
        df=df,
        columnas_grupo=columnas_agrupacion,
        columna_valor=columna_valor,
        agregacion=agregacion,
        incluir_nulos=incluir_nulos,
        ordenar=False,
    )

    return resultado.sort_values(by=columnas_agrupacion).reset_index(drop=True)


# ==========================================================
# Comparación entre periodos
# ==========================================================

# Función para comparar el valor agregado de cada grupo entre dos periodos.
def comparar_periodos(
    df: pd.DataFrame,
    columna_periodo: str,
    columna_grupo: str,
    columna_valor: str,
    periodo_inicial: object,
    periodo_final: object,
    agregacion: str = "sum",
) -> ResultadoComparacionPeriodos:
    """
    Compara grupos entre un periodo inicial y un periodo final.

    Devuelve una tabla con:
    - valor en el periodo inicial
    - valor en el periodo final
    - cambio absoluto
    - cambio porcentual
    """
    tabla_inicial = (
        df[df[columna_periodo] == periodo_inicial]
        .groupby(columna_grupo)[columna_valor]
        .agg(agregacion)
        .reset_index(name="valor_inicial")
    )

    tabla_final = (
        df[df[columna_periodo] == periodo_final]
        .groupby(columna_grupo)[columna_valor]
        .agg(agregacion)
        .reset_index(name="valor_final")
    )

    tabla = (
        tabla_inicial.merge(tabla_final, on=columna_grupo, how="outer")
        .fillna(0)
    )

    tabla["cambio_absoluto"] = tabla["valor_final"] - tabla["valor_inicial"]
    tabla["cambio_porcentual"] = (
        tabla["cambio_absoluto"]
        / tabla["valor_inicial"].replace(0, pd.NA)
    ) * 100

    tabla = tabla.sort_values(
        by="cambio_absoluto",
        ascending=False,
    ).reset_index(drop=True)

    return {
        "tabla": tabla,
        "periodo_inicial": periodo_inicial,
        "periodo_final": periodo_final,
        "columna_periodo": columna_periodo,
        "columna_grupo": columna_grupo,
        "columna_valor": columna_valor,
    }


# ==========================================================
# Reorganización tabular
# ==========================================================

# Función para construir una tabla pivote reutilizable,
# útil para análisis por periodo y categoría.
def construir_tabla_pivote(
    df: pd.DataFrame,
    indice: str | list[str],
    columnas: str,
    columna_valor: str,
    agregacion: str = "sum",
    rellenar_nulos: object = 0,
) -> pd.DataFrame:
    """
    Construye una tabla pivote a partir de un DataFrame.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame de entrada.
    indice : str | list[str]
        Columna o columnas que se usarán como índice.
    columnas : str
        Columna que se expandirá en columnas de la pivote.
    columna_valor : str
        Columna de valores a agregar.
    agregacion : str
        Función de agregación a aplicar.
    rellenar_nulos : object
        Valor con el que se rellenan los nulos en la tabla pivote.

    Devuelve
    --------
    pd.DataFrame
        Tabla pivote resultante.
    """
    indice_lista = _asegurar_lista_columnas(indice)

    tabla_pivote = pd.pivot_table(
        df,
        index=indice_lista,
        columns=columnas,
        values=columna_valor,
        aggfunc=agregacion,
        fill_value=rellenar_nulos,
    )

    return tabla_pivote.reset_index()


# ==========================================================
# Filtros y utilidades de selección
# ==========================================================

# Función para filtrar un DataFrame por un rango de periodos.


def filtrar_por_periodo(
    df: pd.DataFrame,
    columna_periodo: str,
    periodo_minimo: object | None = None,
    periodo_maximo: object | None = None,
) -> pd.DataFrame:
    """
    Filtra un DataFrame por un rango de periodos.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame de entrada.
    columna_periodo : str
        Columna temporal o de periodo.
    periodo_minimo : object | None
        Valor mínimo del periodo a incluir.
    periodo_maximo : object | None
        Valor máximo del periodo a incluir.

    Devuelve
    --------
    pd.DataFrame
        DataFrame filtrado por periodo.
    """
    df_filtrado = df.copy()

    if periodo_minimo is not None:
        df_filtrado = df_filtrado[df_filtrado[columna_periodo]
                                  >= periodo_minimo]

    if periodo_maximo is not None:
        df_filtrado = df_filtrado[df_filtrado[columna_periodo]
                                  <= periodo_maximo]

    return df_filtrado.reset_index(drop=True)


# Función para filtrar un DataFrame por una lista de valores permitidos en una columna.
def filtrar_por_valores(
    df: pd.DataFrame,
    columna: str,
    valores: list[object],
) -> pd.DataFrame:
    """
    Filtra un DataFrame dejando solo filas cuyo valor en la columna
    pertenece a la lista indicada.
    """
    return df[df[columna].isin(valores)].reset_index(drop=True)


# Función para obtener el top N de una tabla ya resumida.
def obtener_top_n(
    df: pd.DataFrame,
    columna_valor: str,
    n: int = 10,
    ascendente: bool = False,
) -> pd.DataFrame:
    """
    Devuelve las primeras N filas de un DataFrame ordenado por una columna de valor.
    """
    return (
        df.sort_values(by=columna_valor, ascending=ascendente)
        .head(n)
        .reset_index(drop=True)
    )
