# Importamos la función de anotaciones futuras para permitir el uso de
# tipos de datos más avanzados y evitar problemas de importación circular en Python 3.7+.
from __future__ import annotations

# Importamos pandas y TypedDict para definir una estructura clara
# del resultado del perfilado del dataset.
from typing import TypedDict

import pandas as pd


# Estructura de resultado del perfilado del dataset
class ResultadoPerfiladoDataset(TypedDict):
    forma: tuple[int, int]
    columnas: list[str]
    tipos_datos: dict[str, str]
    valores_nulos: pd.Series
    total_nulos: int
    filas_duplicadas: int
    rango_temporal: dict[str, object] | None
    resumen_valores_unicos: pd.DataFrame
    resumen_numerico: pd.DataFrame
    resumen_completo: pd.DataFrame


# ==========================================================
# Funciones auxiliares de perfilado
# ==========================================================

# Función para resumir valores nulos por columna,
# devolviendo una Serie ordenada de mayor a menor.
def resumir_valores_nulos(df: pd.DataFrame) -> pd.Series:
    """
    Devuelve la cantidad de valores nulos por columna.
    """
    # La función isna() devuelve un DataFrame booleano indicando dónde hay nulos,
    # sum() cuenta los nulos por columna, y sort_values() ordena el resultado de mayor a menor.
    return df.isna().sum().sort_values(ascending=False)


# Función para contar filas duplicadas del DataFrame.
def contar_filas_duplicadas(df: pd.DataFrame) -> int:
    """
    Devuelve la cantidad de filas duplicadas.
    """
    # La función duplicated() devuelve un Series booleano indicando qué filas son duplicadas,
    # y sum() cuenta cuántas filas son duplicadas.
    return int(df.duplicated().sum())


# Función para obtener un resumen de valores únicos por columna,
# útil sobre todo para columnas categóricas o identificadores.
def resumir_valores_unicos(
    df: pd.DataFrame,
    columnas: list[str] | None = None,
) -> pd.DataFrame:
    """
    Devuelve un DataFrame con la cantidad de valores únicos por columna.
    """
    # Si no se especifican columnas, se resumen todas las columnas del DataFrame.
    columnas_objetivo = columnas or list(df.columns)

    # Construimos una lista de diccionarios con el nombre de la columna y la cantidad de valores únicos.
    filas_resumen: list[dict[str, object]] = []

    # Iteramos sobre las columnas objetivo y contamos los valores únicos usando nunique(), ignorando los nulos.
    for nombre_columna in columnas_objetivo:
        # Si la columna no existe en el DataFrame, la saltamos para evitar errores.
        if nombre_columna not in df.columns:
            continue

        # Agregamos un diccionario al resumen con el nombre de la columna y la cantidad de valores únicos.
        filas_resumen.append({
            "columna": nombre_columna,
            "valores_unicos": int(df[nombre_columna].nunique(dropna=True)),
        })

    # Convertimos la lista de diccionarios en un DataFrame para una presentación más clara y ordenada.
    return pd.DataFrame(filas_resumen)


# Función para detectar un rango temporal básico si se indica una columna temporal.
def obtener_rango_temporal(
    df: pd.DataFrame,
    columna_temporal: str | None = None,
) -> dict[str, object] | None:
    """
    Devuelve información básica del rango temporal de una columna si existe.
    """
    # Si no se indica una columna temporal, o si la columna no existe, devolvemos None.
    if not columna_temporal:
        return None

    # Si la columna temporal no existe en el DataFrame, también devolvemos None para evitar errores.
    if columna_temporal not in df.columns:
        return None

    # Extraemos la serie temporal de la columna indicada,
    # eliminando los valores nulos (.dropna()) para evitar problemas al calcular el mínimo, máximo y valores únicos.
    serie = df[columna_temporal].dropna()

    # Si la serie temporal está vacía después de eliminar los nulos,
    # devolvemos un resultado con mínimos, máximos y valores únicos como None o 0 para evitar errores al calcular estos valores.
    if serie.empty:
        return {
            "columna": columna_temporal,
            "minimo": None,
            "maximo": None,
            "periodos_unicos": 0,
        }

    # Si la serie no está vacía, calculamos el mínimo, máximo y cantidad de periodos únicos,
    # y devolvemos un diccionario con esta información.
    # EJ: 
    # {
    # "columna": "anio",
    # "minimo": 2015,
    # "maximo": 2024,
    # "periodos_unicos": 10,
    # }
    return {
        "columna": columna_temporal,
        "minimo": serie.min(),
        "maximo": serie.max(),
        "periodos_unicos": int(serie.nunique()),
    }


# ==========================================================
# Perfilado principal del dataset
# ==========================================================

# Función principal para perfilar un DataFrame y devolver un resultado
# estructurado reutilizable para análisis posteriores.
def perfilar_dataset(
    df: pd.DataFrame,
    columna_temporal: str | None = None,
) -> ResultadoPerfiladoDataset:
    """
    Genera un perfil general del dataset.

    Incluye:
    - forma del DataFrame
    - nombres de columnas
    - tipos de datos
    - valores nulos
    - filas duplicadas
    - rango temporal si se indica una columna temporal
    - resumen de valores únicos por columna
    - resumen numérico
    - resumen completo
    """
    # Resumimos los valores nulos por columna usando la función auxiliar definida anteriormente.
    valores_nulos = resumir_valores_nulos(df)
    
    # Obtenemos el rango temporal si se indica una columna temporal, usando la función auxiliar definida anteriormente.
    rango_temporal = obtener_rango_temporal(
        df, columna_temporal=columna_temporal)
    
    # Obtenemos un resumen de valores únicos por columna.
    # Ej: "columna": "categoria", "valores_unicos": 5
    resumen_valores_unicos = resumir_valores_unicos(df)
    
    # Construimos un diccionario de tipos de datos por columna, convirtiendo los tipos a cadenas para una presentación más clara.
    tipos_datos: dict[str, str] = {
        str(nombre_columna): str(tipo_dato)
        for nombre_columna, tipo_dato in df.dtypes.items()
    }
    
    # Devolvemos un diccionario con toda la información del perfilado, 
    # utilizando la estructura definida por ResultadoPerfiladoDataset para mayor claridad y reutilización.
    return {
        "forma": df.shape,
        "columnas": list(df.columns),
        "tipos_datos": tipos_datos,
        "valores_nulos": valores_nulos,
        "total_nulos": int(valores_nulos.sum()),
        "filas_duplicadas": contar_filas_duplicadas(df),
        "rango_temporal": rango_temporal,
        "resumen_valores_unicos": resumen_valores_unicos,
        "resumen_numerico": df.describe(),
        "resumen_completo": df.describe(include="all"),
    }
