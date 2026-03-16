# Importamos la función de anotaciones futuras para permitir el uso de
# tipos de datos más avanzados y evitar problemas de importación circular en Python 3.7+.
from __future__ import annotations

# Importamos módulos necesarios para normalización y validación de esquemas de DataFrames, incluyendo expresiones regulares,
# manipulación de texto, y tipos de datos de pandas. También definimos una estructura de resultado para la validación del esquema.
import re
import unicodedata
from typing import TypedDict

# Importamos pandas y funciones de detección de tipos para validaciones específicas
import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
    is_string_dtype,
)

# Estructura de resultado de validación del esquema


class SchemaValidationResult(TypedDict):
    is_valid: bool
    data: pd.DataFrame
    original_columns: list[str]
    columns: list[str]
    missing_columns: list[str]
    unexpected_columns: list[str]
    duplicate_columns: list[str]
    dtype_issues: dict[str, dict[str, str]]
    renamed_columns: dict[str, str]
    alias_conflicts: dict[str, list[str]]


# ==========================================================
# Utilidades internas de normalización
# ==========================================================

# Función para normalizar texto a un formato canónico, útil para nombres de columnas y claves de alias.
def normalize_text(value: str) -> str:
    """
    Normaliza un texto para usarlo como nombre de columna o clave canónica.

    Reglas aplicadas:
    - quita espacios al inicio y al final
    - convierte a minúsculas
    - elimina tildes y caracteres diacríticos
    - reemplaza separadores comunes por "_"
    - elimina caracteres no alfanuméricos innecesarios
    - colapsa múltiples "_" en uno solo
    """

    # Si el valor no es un string, lo convertimos a string para evitar errores en la normalización.
    if not isinstance(value, str):  # type: ignore
        value = str(value)

    # Normalizamos el string resultante
    value = value.strip().lower()

    # Eliminar tildes / diacríticos
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))

    # Reemplazar separadores comunes por "_"
    value = re.sub(r"[\s\-/]+", "_", value)

    # Eliminar cualquier carácter que no sea alfanumérico o "_"
    value = re.sub(r"[^a-z0-9_]", "", value)

    # Colapsar múltiples "_" y limpiar extremos
    value = re.sub(r"_+", "_", value).strip("_")

    return value

# Funciones internas para normalizar alias y tipos esperados, asegurando que la validación trabaje con nombres consistentes.

# Función para normalizar el alias_map, aplicando la misma lógica de normalización a las claves canónicas y a los aliases.
def _normalize_alias_map(alias_map: dict[str, list[str]] | None) -> dict[str, list[str]]:
    """
    Devuelve un alias_map normalizado para trabajar siempre con nombres consistentes.
    """

    # Si no se pasa ningún alias_map, devolvemos un diccionario vacío para evitar invalidar el esquema por falta de referencia.
    if not alias_map:
        return {}

    # Normalizamos tanto las claves canónicas como los aliases en el
    # alias_map para asegurar que la validación trabaje con nombres consistentes,
    # lo cual es crucial para que la resolución de alias funcione correctamente
    # y no reporte falsos positivos por diferencias de formato en los nombres de columnas.
    normalized_map: dict[str, list[str]] = {}

    # Iteramos sobre cada nombre canónico y sus aliases en el alias_map original,
    # normalizando ambos para construir el alias_map normalizado.
    for canonical_name, aliases in alias_map.items():
        normalized_canonical = normalize_text(canonical_name)
        normalized_aliases = [normalize_text(alias) for alias in aliases]
        normalized_map[normalized_canonical] = normalized_aliases

    # Retornamos el alias_map normalizado, que ahora contiene claves canónicas y aliases en un formato consistente.
    return normalized_map


# Normalización de tipos esperados, asegurando que las claves sean consistentes con la normalización de columnas.
def _normalize_expected_dtypes(
    expected_dtypes: dict[str, str] | None,
) -> dict[str, str]:
    """
    Normaliza las claves del diccionario de tipos esperados.
    """

    # Si no se pasa ningún tipo esperado,
    # devolvemos un diccionario vacío para evitar problemas de validación posteriores.
    if not expected_dtypes:
        return {}

    # Normalizamos las claves del diccionario de tipos esperados para que coincidan
    # con la normalización aplicada a los nombres de columnas.
    return {
        normalize_text(column_name): expected_dtype
        for column_name, expected_dtype in expected_dtypes.items()
    }


# ==========================================================
# Normalización de columnas
# ==========================================================

# Función para normalizar los nombres de columnas de un DataFrame,
# aplicando la misma lógica de normalización que para los alias y tipos esperados.
def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Devuelve una copia del DataFrame con nombres de columnas normalizados.
    """
    normalized_df = df.copy()
    normalized_df.columns = [normalize_text(
        column) for column in normalized_df.columns]
    return normalized_df

# Función para detectar columnas duplicadas después de la normalización,
# lo cual puede indicar problemas de esquema o datos.
def find_duplicate_columns(df: pd.DataFrame) -> list[str]:
    """
    Detecta nombres de columnas duplicados.
    """
    duplicated_mask = pd.Index(df.columns).duplicated(keep=False)
    duplicated_columns = pd.Index(df.columns)[duplicated_mask].tolist()
    return sorted(set(duplicated_columns))


# ==========================================================
# Resolución de alias
# ==========================================================

# Función para resolver columnas alias al nombre canónico definido en alias_map,
# aplicando reglas para evitar conflictos y reportar problemas de alias.
def resolve_column_aliases(
    df: pd.DataFrame,
    alias_map: dict[str, list[str]] | None,
) -> tuple[pd.DataFrame, dict[str, str], dict[str, list[str]]]:
    """
    Renombra columnas alias al nombre canónico definido en alias_map.

    Devuelve:
    - DataFrame con columnas renombradas
    - diccionario {alias_encontrado: nombre_canonico}
    - diccionario de conflictos por alias:
      cuando existen varias columnas que podrían mapear al mismo nombre canónico

    Reglas:
    - si la columna canónica ya existe, no se renombra ningún alias adicional
      para evitar sobrescribir o duplicar sin control
    - si aparecen varios aliases para la misma columna canónica y la canónica no existe,
      se renombra solo el primero y se reportan los demás como conflicto
    """

    # Normalizamos el alias_map para asegurar que trabajamos con nombres consistentes.
    normalized_alias_map = _normalize_alias_map(alias_map)
    # Creamos una copia del DataFrame para trabajar sin modificar el original.
    working_df = df.copy()

    # Diccionario para rastrear qué columnas fueron renombradas y a qué nombre canónico.
    renamed_columns: dict[str, str] = {}
    # Diccionario para rastrear conflictos de alias, donde una misma columna canónica tiene múltiples aliases encontrados.
    alias_conflicts: dict[str, list[str]] = {}

    # Obtenemos la lista actual de columnas para iterar y comparar con el alias_map.
    current_columns = list(working_df.columns)

    # Iteramos sobre cada nombre canónico y sus aliases para detectar coincidencias en las columnas actuales.
    for canonical_name, aliases in normalized_alias_map.items():
        # Buscamos columnas que coincidan con el nombre canónico o cualquiera de sus aliases.
        matching_columns = [
            column_name
            for column_name in current_columns
            if column_name == canonical_name or column_name in aliases
        ]

        # Si no se encuentra ninguna columna que coincida con el nombre canónico o sus aliases,
        # simplemente continuamos con el siguiente.
        if not matching_columns:
            continue

        # Si la columna canónica ya existe entre las columnas actuales, no renombramos ningún alias para esa canónica,
        # pero sí reportamos si hay aliases adicionales que podrían haber mapeado a esa canónica,
        # ya que podrían indicar un problema de datos o esquema.
        # Ej: si canonical_name="anio" ya existe, y también se encuentra "año"
        # como alias, reportamos "año" como conflicto de alias para "anio".
        if canonical_name in matching_columns:
            extra_aliases = [
                column for column in matching_columns if column != canonical_name]
            if extra_aliases:
                alias_conflicts[canonical_name] = extra_aliases
            continue

        # Si la columna canónica no existe pero sí se encuentran aliases, renombramos el primer alias encontrado a la canónica,
        # y reportamos cualquier alias adicional como conflicto, ya que no se renombrarán para evitar sobrescribir sin control.
        source_column = matching_columns[0]
        renamed_columns[source_column] = canonical_name

        # Si hay más de un alias que coincide con la misma columna canónica, reportamos los aliases adicionales como conflictos.
        remaining_aliases = matching_columns[1:]
        if remaining_aliases:
            alias_conflicts[canonical_name] = remaining_aliases

    # Aplicamos los renombrados al DataFrame, asegurándonos de no modificar el orden de las columnas.
    if renamed_columns:
        working_df = working_df.rename(columns=renamed_columns)

    # Actualizamos la lista de columnas actuales después de renombrar para reflejar los cambios en el DataFrame,
    # lo cual es importante para detectar correctamente los conflictos de alias en iteraciones posteriores.
    return working_df, renamed_columns, alias_conflicts


# ==========================================================
# Validaciones específicas
# ==========================================================

# Función para validar que todas las columnas obligatorias estén presentes en el DataFrame,
# devolviendo una lista de las columnas faltantes para reportar en el resultado de validación del esquema.
def validate_required_columns(
    df: pd.DataFrame,
    required_columns: list[str] | None,
) -> list[str]:
    """
    Devuelve la lista de columnas obligatorias faltantes.
    """

    # Si no se pasa ninguna columna obligatoria, devolvemos una lista vacía para evitar invalidar el esquema por falta de referencia.
    if not required_columns:
        return []

    # Normalizamos los nombres de las columnas obligatorias para compararlos con los
    # nombres de columnas del DataFrame, que también han sido normalizados.
    normalized_required = [normalize_text(
        column_name) for column_name in required_columns]

    # Creamos un conjunto de las columnas existentes en el DataFrame para una búsqueda eficiente de las columnas obligatorias.
    existing_columns = set(df.columns)

    # Detectamos qué columnas obligatorias faltan comparando
    # la lista de columnas normalizadas con el conjunto de columnas existentes.
    missing_columns = [
        column_name
        for column_name in normalized_required
        if column_name not in existing_columns
    ]

    # Devolvemos la lista de columnas obligatorias faltantes,
    # lo cual es un indicador clave para determinar si el esquema es válido o no.
    return missing_columns

# Función para validar que los tipos de datos de las columnas coincidan con los tipos esperados definidos en expected_dtypes,
# utilizando funciones de detección de tipos de pandas para una validación más flexible y práctica.


def _dtype_matches(series: pd.Series, expected_dtype: str) -> bool:
    """
    Evalúa si la serie coincide con el tipo esperado.

    Tipos prácticos soportados:
    - "numeric"
    - "string"
    - "datetime"
    - "bool"

    También acepta tipos exactos como:
    - "int64"
    - "float64"
    - "object"
    - "category"
    """

    # Normalizamos el tipo esperado para facilitar la comparación,
    # permitiendo variaciones comunes en la forma de escribir los tipos.
    expected = expected_dtype.strip().lower()

    # Utilizamos funciones de detección de tipos de pandas
    # para validar tipos prácticos como "numeric", "string", "datetime" y "bool",
    # lo cual es más flexible que comparar con tipos exactos,
    # ya que permite validar cualquier tipo numérico o de texto sin tener que especificar cada variante.
    if expected in {"numeric", "number", "int", "integer", "float"}:
        return is_numeric_dtype(series)

    # Para tipos de texto, consideramos tanto string_dtype como object_dtype,
    # ya que en pandas los textos pueden ser representados como object.
    if expected in {"string", "str", "text"}:
        return is_string_dtype(series) or is_object_dtype(series)

    # Para tipos de fecha y hora, utilizamos is_datetime64_any_dtype para cubrir
    # todas las variantes de datetime que pandas puede manejar.
    if expected in {"datetime", "datetime64", "date"}:
        return is_datetime64_any_dtype(series)

    # Para tipos booleanos, utilizamos is_bool_dtype para validar cualquier tipo booleano reconocido por pandas.
    if expected in {"bool", "boolean"}:
        return is_bool_dtype(series)

    # Para tipos específicos, comparamos directamente con el dtype de la serie.
    return str(series.dtype).lower() == expected

# Función principal para validar que los tipos de datos
# de las columnas coincidan con los tipos esperados definidos en expected_dtypes,


def validate_expected_dtypes(
    df: pd.DataFrame,
    expected_dtypes: dict[str, str] | None,
) -> dict[str, dict[str, str]]:
    """
    Devuelve un diccionario con problemas de tipos detectados.

    Formato:
    {
        "anio": {
            "expected": "numeric",
            "current": "object"
        }
    }
    """

    # Si no se pasa ningún tipo esperado, devolvemos un diccionario vacío para evitar invalidar el esquema por falta de referencia.
    if not expected_dtypes:
        return {}

    # Normalizamos las claves del diccionario de tipos esperados para asegurarnos
    # de que coincidan con la normalización aplicada a los nombres de columnas,
    # lo cual es crucial para que la validación funcione correctamente y
    # no reporte falsos positivos por diferencias de formato en los nombres de columnas.
    normalized_expected_dtypes = _normalize_expected_dtypes(expected_dtypes)

    # Diccionario para rastrear problemas de tipos detectados, donde cada clave es el nombre de la columna con un problema,
    # y el valor es otro diccionario con el tipo esperado y el tipo actual detectado en el DataFrame,
    # lo cual proporciona información detallada para diagnosticar y corregir problemas de tipos en el esquema de datos.
    dtype_issues: dict[str, dict[str, str]] = {}

    # Iteramos sobre cada columna y su tipo esperado para validar el tipo de datos de la columna en el DataFrame
    for column_name, expected_dtype in normalized_expected_dtypes.items():
        # Si la columna esperada no existe en el DataFrame,
        # no podemos validar su tipo, así que simplemente continuamos con la siguiente columna.
        if column_name not in df.columns:
            continue

        # Obtenemos el tipo actual de la columna en el DataFrame
        # como una cadena para reportar en caso de que no coincida con el tipo esperado.
        current_dtype = str(df[column_name].dtype)

        # Utilizamos la función _dtype_matches para evaluar si el tipo de la columna coincide con el tipo esperado,
        # lo cual permite una validación más flexible y práctica,
        # ya que puede manejar tanto tipos prácticos como tipos
        # específicos sin requerir que el usuario especifique cada variante de tipo.
        if not _dtype_matches(df[column_name], expected_dtype):
            dtype_issues[column_name] = {
                "expected": expected_dtype,
                "current": current_dtype,
            }

    return dtype_issues

# Función para detectar columnas que no pertenecen al conjunto conocido del esquema,
# el cual se construye a partir de las columnas obligatorias, las claves canónicas de alias_map
# y las claves de expected_dtypes, lo cual ayuda a identificar columnas inesperadas que
# podrían indicar problemas de datos o esquema, especialmente cuando allow_extra_columns
# es False en la validación del esquema. Si no se pasa ninguna referencia de esquema,
# devuelve una lista vacía para evitar invalidar el esquema por falta de referencia.


def detect_unexpected_columns(
    df: pd.DataFrame,
    required_columns: list[str] | None = None,
    alias_map: dict[str, list[str]] | None = None,
    expected_dtypes: dict[str, str] | None = None,
) -> list[str]:
    """
    Detecta columnas que no pertenecen al conjunto conocido del esquema.

    El conjunto conocido se construye a partir de:
    - required_columns
    - claves canónicas de alias_map
    - claves de expected_dtypes

    Si no se pasa ninguna referencia de esquema, devuelve lista vacía.
    """

    # Construimos un conjunto de nombres de columnas conocidos a partir de las columnas obligatorias
    known_columns: set[str] = set()

    # Agregamos las columnas obligatorias al conjunto de columnas conocidas,
    # normalizando sus nombres para asegurar consistencia con los nombres de columnas del DataFrame.
    if required_columns:
        known_columns.update(normalize_text(column_name)
                             for column_name in required_columns)

    # Si se pasan columnas obligatorias, asumimos que el esquema está definido
    # y no reportamos columnas inesperadas para evitar invalidar el esquema por falta de referencia,
    # ya que la validación se basará en las columnas obligatorias como referencia principal
    # para determinar qué columnas son esperadas.
    if alias_map:
        known_columns.update(_normalize_alias_map(alias_map).keys())

    # Si se pasa un alias_map, asumimos que el esquema está definido y
    # no reportamos columnas inesperadas para evitar invalidar el esquema por falta de referencia,
    # ya que la validación se basará en las claves canónicas del alias_map
    # como referencia principal para determinar qué columnas son esperadas.
    if expected_dtypes:
        known_columns.update(
            _normalize_expected_dtypes(expected_dtypes).keys())

    # Si se pasan tipos esperados, asumimos que el esquema está definido
    # y no reportamos columnas inesperadas para evitar invalidar el esquema por falta de referencia,
    # ya que la validación se basará en las claves de expected_dtypes
    # como referencia principal para determinar qué columnas son esperadas.
    if not known_columns:
        return []

    # Detectamos columnas inesperadas comparando los nombres de columnas del DataFrame con el conjunto de columnas conocidas,
    # lo cual ayuda a identificar columnas que no pertenecen al esquema definido
    # por las referencias proporcionadas, y que podrían indicar problemas de datos
    # o esquema, especialmente cuando allow_extra_columns es False en la validación del esquema.
    return [column_name for column_name in df.columns if column_name not in known_columns]


# ==========================================================
# Validación principal del esquema
# ==========================================================

# Función principal para validar el esquema de un DataFrame, que integra todas las validaciones anteriores
# y devuelve un resultado estructurado con información detallada sobre la validez del esquema,
# las columnas originales, las columnas después de la normalización y resolución de alias,
# las columnas faltantes, las columnas inesperadas, los duplicados, los problemas de tipos,
# los renombrados realizados y los conflictos de alias detectados,
# lo cual proporciona una visión completa del estado del esquema del DataFrame
# y facilita la identificación y corrección de problemas en los datos.
def validate_schema(
    df: pd.DataFrame,
    required_columns: list[str] | None = None,
    alias_map: dict[str, list[str]] | None = None,
    expected_dtypes: dict[str, str] | None = None,
    allow_extra_columns: bool = True,
) -> SchemaValidationResult:
    """
    Valida el esquema de un DataFrame y devuelve un resultado estructurado.

    Flujo:
    1. normaliza nombres de columnas
    2. detecta duplicados
    3. resuelve alias
    4. valida columnas obligatorias
    5. valida tipos esperados
    6. detecta columnas inesperadas

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame de entrada.
    required_columns : list[str] | None
        Lista de columnas obligatorias.
    alias_map : dict[str, list[str]] | None
        Mapa de aliases por nombre canónico.
    expected_dtypes : dict[str, str] | None
        Tipos esperados por columna.
    allow_extra_columns : bool
        Si es False, columnas inesperadas invalidan el esquema.

    Devuelve
    --------
    dict
        Resultado estructurado de la validación.
    """
    original_columns = list(df.columns)

    # Normalizamos las columnas del DataFrame para trabajar con nombres consistentes en todas las validaciones posteriores.
    working_df = normalize_column_names(df)

    # Detectamos columnas duplicadas después de la normalización,
    # lo cual puede indicar problemas de esquema o datos que deben ser corregidos para garantizar la validez del esquema.
    duplicate_columns = find_duplicate_columns(working_df)

    # Resolvemos columnas alias al nombre canónico definido en alias_map,
    # aplicando reglas para evitar conflictos y reportar problemas de alias.
    working_df, renamed_columns, alias_conflicts = resolve_column_aliases(
        working_df,
        alias_map=alias_map,
    )

    # Validamos que todas las columnas obligatorias estén presentes en el DataFrame,
    # devolviendo una lista de las columnas faltantes para reportar en el resultado de validación del esquema.
    missing_columns = validate_required_columns(
        working_df,
        required_columns=required_columns,
    )

    # Validamos que los tipos de datos de las columnas coincidan con los tipos esperados definidos en expected_dtypes,
    # utilizando funciones de detección de tipos de pandas para una validación más flexible y práctica,
    # y devolviendo un diccionario con problemas de tipos detectados.
    dtype_issues = validate_expected_dtypes(
        working_df,
        expected_dtypes=expected_dtypes,
    )

    # Detectamos columnas que no pertenecen al conjunto conocido del esquema.
    unexpected_columns = detect_unexpected_columns(
        working_df,
        required_columns=required_columns,
        alias_map=alias_map,
        expected_dtypes=expected_dtypes,
    )

    # Determinamos si el esquema es válido o no en función de los resultados de las validaciones anteriores,
    # aplicando la lógica de validación que considera el esquema como válido solo si no hay
    # columnas obligatorias faltantes, no hay problemas de tipos, no hay columnas duplicadas,
    # no hay conflictos de alias, y si allow_extra_columns es False, no hay columnas inesperadas,
    # lo cual garantiza que el esquema cumple con las expectativas definidas por las referencias proporcionadas
    # y que no contiene problemas que podrían afectar la calidad o integridad de los datos.
    is_valid = (
        len(missing_columns) == 0
        and len(dtype_issues) == 0
        and len(duplicate_columns) == 0
        and len(alias_conflicts) == 0
        and (allow_extra_columns or len(unexpected_columns) == 0)
    )

    # Devolvemos un resultado estructurado con toda la información relevante sobre la validación del esquema,
    # lo cual proporciona una visión completa del estado del esquema del DataFrame
    # y facilita la identificación y corrección de problemas en los datos.
    return {
        "is_valid": is_valid,
        "data": working_df,
        "original_columns": original_columns,
        "columns": list(working_df.columns),
        "missing_columns": missing_columns,
        "unexpected_columns": unexpected_columns,
        "duplicate_columns": duplicate_columns,
        "dtype_issues": dtype_issues,
        "renamed_columns": renamed_columns,
        "alias_conflicts": alias_conflicts,
    }
