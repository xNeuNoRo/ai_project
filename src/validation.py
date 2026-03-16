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


class ResultadoValidacionEsquema(TypedDict):
    es_valido: bool
    datos: pd.DataFrame
    columnas_originales: list[str]
    columnas: list[str]
    columnas_faltantes: list[str]
    columnas_inesperadas: list[str]
    columnas_duplicadas: list[str]
    problemas_tipos: dict[str, dict[str, str]]
    columnas_renombradas: dict[str, str]
    conflictos_alias: dict[str, list[str]]


# ==========================================================
# Utilidades internas de normalización
# ==========================================================

# Función para normalizar texto a un formato canónico, útil para nombres de columnas y claves de alias.
def normalizar_texto(valor: str) -> str:
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
    if not isinstance(valor, str):  # type: ignore
        valor = str(valor)

    # Normalizamos el string resultante
    valor = valor.strip().lower()

    # Eliminar tildes / diacríticos
    valor = unicodedata.normalize("NFKD", valor)
    valor = "".join(caracter for caracter in valor if not unicodedata.combining(caracter))

    # Reemplazar separadores comunes por "_"
    valor = re.sub(r"[\s\-/]+", "_", valor)

    # Eliminar cualquier carácter que no sea alfanumérico o "_"
    valor = re.sub(r"[^a-z0-9_]", "", valor)

    # Colapsar múltiples "_" y limpiar extremos
    valor = re.sub(r"_+", "_", valor).strip("_")

    return valor

# Funciones internas para normalizar alias y tipos esperados, asegurando que la validación trabaje con nombres consistentes.

# Función para normalizar el mapa_alias, aplicando la misma lógica de normalización a las claves canónicas y a los alias.
def _normalizar_mapa_alias(mapa_alias: dict[str, list[str]] | None) -> dict[str, list[str]]:
    """
    Devuelve un mapa_alias normalizado para trabajar siempre con nombres consistentes.
    """

    # Si no se pasa ningún mapa_alias, devolvemos un diccionario vacío para evitar invalidar el esquema por falta de referencia.
    if not mapa_alias:
        return {}

    # Normalizamos tanto las claves canónicas como los alias en el
    # mapa_alias para asegurar que la validación trabaje con nombres consistentes,
    # lo cual es crucial para que la resolución de alias funcione correctamente
    # y no reporte falsos positivos por diferencias de formato en los nombres de columnas.
    mapa_normalizado: dict[str, list[str]] = {}

    # Iteramos sobre cada nombre canónico y sus alias en el mapa_alias original,
    # normalizando ambos para construir el mapa_alias normalizado.
    for nombre_canonico, lista_alias in mapa_alias.items():
        nombre_canonico_normalizado = normalizar_texto(nombre_canonico)
        alias_normalizados = [normalizar_texto(alias) for alias in lista_alias]
        mapa_normalizado[nombre_canonico_normalizado] = alias_normalizados

    # Retornamos el mapa_alias normalizado, que ahora contiene claves canónicas y alias en un formato consistente.
    return mapa_normalizado


# Normalización de tipos esperados, asegurando que las claves sean consistentes con la normalización de columnas.
def _normalizar_tipos_esperados(
    tipos_esperados: dict[str, str] | None,
) -> dict[str, str]:
    """
    Normaliza las claves del diccionario de tipos esperados.
    """

    # Si no se pasa ningún tipo esperado,
    # devolvemos un diccionario vacío para evitar problemas de validación posteriores.
    if not tipos_esperados:
        return {}

    # Normalizamos las claves del diccionario de tipos esperados para que coincidan
    # con la normalización aplicada a los nombres de columnas.
    return {
        normalizar_texto(nombre_columna): tipo_esperado
        for nombre_columna, tipo_esperado in tipos_esperados.items()
    }


# ==========================================================
# Normalización de columnas
# ==========================================================

# Función para normalizar los nombres de columnas de un DataFrame,
# aplicando la misma lógica de normalización que para los alias y tipos esperados.
def normalizar_nombres_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Devuelve una copia del DataFrame con nombres de columnas normalizados.
    """
    df_normalizado = df.copy()
    df_normalizado.columns = [normalizar_texto(
        columna) for columna in df_normalizado.columns]
    return df_normalizado

# Función para detectar columnas duplicadas después de la normalización,
# lo cual puede indicar problemas de esquema o datos.
def detectar_columnas_duplicadas(df: pd.DataFrame) -> list[str]:
    """
    Detecta nombres de columnas duplicados.
    """
    mascara_duplicados = pd.Index(df.columns).duplicated(keep=False)
    columnas_duplicadas = pd.Index(df.columns)[mascara_duplicados].tolist()
    return sorted(set(columnas_duplicadas))


# ==========================================================
# Resolución de alias
# ==========================================================

# Función para resolver columnas alias al nombre canónico definido en mapa_alias,
# aplicando reglas para evitar conflictos y reportar problemas de alias.
def resolver_alias_columnas(
    df: pd.DataFrame,
    mapa_alias: dict[str, list[str]] | None,
) -> tuple[pd.DataFrame, dict[str, str], dict[str, list[str]]]:
    """
    Renombra columnas alias al nombre canónico definido en mapa_alias.

    Devuelve:
    - DataFrame con columnas renombradas
    - diccionario {alias_encontrado: nombre_canonico}
    - diccionario de conflictos por alias:
      cuando existen varias columnas que podrían mapear al mismo nombre canónico

    Reglas:
    - si la columna canónica ya existe, no se renombra ningún alias adicional
      para evitar sobrescribir o duplicar sin control
    - si aparecen varios alias para la misma columna canónica y la canónica no existe,
      se renombra solo el primero y se reportan los demás como conflicto
    """

    # Normalizamos el mapa_alias para asegurar que trabajamos con nombres consistentes.
    mapa_alias_normalizado = _normalizar_mapa_alias(mapa_alias)
    # Creamos una copia del DataFrame para trabajar sin modificar el original.
    df_trabajo = df.copy()

    # Diccionario para rastrear qué columnas fueron renombradas y a qué nombre canónico.
    columnas_renombradas: dict[str, str] = {}
    # Diccionario para rastrear conflictos de alias, donde una misma columna canónica tiene múltiples alias encontrados.
    conflictos_alias: dict[str, list[str]] = {}

    # Obtenemos la lista actual de columnas para iterar y comparar con el mapa_alias.
    columnas_actuales = list(df_trabajo.columns)

    # Iteramos sobre cada nombre canónico y sus alias para detectar coincidencias en las columnas actuales.
    for nombre_canonico, lista_alias in mapa_alias_normalizado.items():
        # Buscamos columnas que coincidan con el nombre canónico o cualquiera de sus alias.
        columnas_coincidentes = [
            nombre_columna
            for nombre_columna in columnas_actuales
            if nombre_columna == nombre_canonico or nombre_columna in lista_alias
        ]

        # Si no se encuentra ninguna columna que coincida con el nombre canónico o sus alias,
        # simplemente continuamos con el siguiente.
        if not columnas_coincidentes:
            continue

        # Si la columna canónica ya existe entre las columnas actuales, no renombramos ningún alias para esa canónica,
        # pero sí reportamos si hay alias adicionales que podrían haber mapeado a esa canónica,
        # ya que podrían indicar un problema de datos o esquema.
        # Ej: si nombre_canonico="anio" ya existe, y también se encuentra "año"
        # como alias, reportamos "año" como conflicto de alias para "anio".
        if nombre_canonico in columnas_coincidentes:
            alias_extra = [
                columna for columna in columnas_coincidentes if columna != nombre_canonico]
            if alias_extra:
                conflictos_alias[nombre_canonico] = alias_extra
            continue

        # Si la columna canónica no existe pero sí se encuentran alias, renombramos el primer alias encontrado a la canónica,
        # y reportamos cualquier alias adicional como conflicto, ya que no se renombrarán para evitar sobrescribir sin control.
        columna_origen = columnas_coincidentes[0]
        columnas_renombradas[columna_origen] = nombre_canonico

        # Si hay más de un alias que coincide con la misma columna canónica, reportamos los alias adicionales como conflictos.
        alias_restantes = columnas_coincidentes[1:]
        if alias_restantes:
            conflictos_alias[nombre_canonico] = alias_restantes

    # Aplicamos los renombrados al DataFrame, asegurándonos de no modificar el orden de las columnas.
    if columnas_renombradas:
        df_trabajo = df_trabajo.rename(columns=columnas_renombradas)

    # Actualizamos la lista de columnas actuales después de renombrar para reflejar los cambios en el DataFrame,
    # lo cual es importante para detectar correctamente los conflictos de alias en iteraciones posteriores.
    return df_trabajo, columnas_renombradas, conflictos_alias


# ==========================================================
# Validaciones específicas
# ==========================================================

# Función para validar que todas las columnas obligatorias estén presentes en el DataFrame,
# devolviendo una lista de las columnas faltantes para reportar en el resultado de validación del esquema.
def validar_columnas_obligatorias(
    df: pd.DataFrame,
    columnas_obligatorias: list[str] | None,
) -> list[str]:
    """
    Devuelve la lista de columnas obligatorias faltantes.
    """

    # Si no se pasa ninguna columna obligatoria, devolvemos una lista vacía para evitar invalidar el esquema por falta de referencia.
    if not columnas_obligatorias:
        return []

    # Normalizamos los nombres de las columnas obligatorias para compararlos con los
    # nombres de columnas del DataFrame, que también han sido normalizados.
    columnas_obligatorias_normalizadas = [normalizar_texto(
        nombre_columna) for nombre_columna in columnas_obligatorias]

    # Creamos un conjunto de las columnas existentes en el DataFrame para una búsqueda eficiente de las columnas obligatorias.
    columnas_existentes = set(df.columns)

    # Detectamos qué columnas obligatorias faltan comparando
    # la lista de columnas normalizadas con el conjunto de columnas existentes.
    columnas_faltantes = [
        nombre_columna
        for nombre_columna in columnas_obligatorias_normalizadas
        if nombre_columna not in columnas_existentes
    ]

    # Devolvemos la lista de columnas obligatorias faltantes,
    # lo cual es un indicador clave para determinar si el esquema es válido o no.
    return columnas_faltantes

# Función para validar que los tipos de datos de las columnas coincidan con los tipos esperados definidos en tipos_esperados,
# utilizando funciones de detección de tipos de pandas para una validación más flexible y práctica.


def _tipo_coincide(serie: pd.Series, tipo_esperado: str) -> bool:
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
    tipo_esperado_normalizado = tipo_esperado.strip().lower()

    # Utilizamos funciones de detección de tipos de pandas
    # para validar tipos prácticos como "numeric", "string", "datetime" y "bool",
    # lo cual es más flexible que comparar con tipos exactos,
    # ya que permite validar cualquier tipo numérico o de texto sin tener que especificar cada variante.
    if tipo_esperado_normalizado in {"numeric", "number", "int", "integer", "float"}:
        return is_numeric_dtype(serie)

    # Para tipos de texto, consideramos tanto string_dtype como object_dtype,
    # ya que en pandas los textos pueden ser representados como object.
    if tipo_esperado_normalizado in {"string", "str", "text"}:
        return is_string_dtype(serie) or is_object_dtype(serie)

    # Para tipos de fecha y hora, utilizamos is_datetime64_any_dtype para cubrir
    # todas las variantes de datetime que pandas puede manejar.
    if tipo_esperado_normalizado in {"datetime", "datetime64", "date"}:
        return is_datetime64_any_dtype(serie)

    # Para tipos booleanos, utilizamos is_bool_dtype para validar cualquier tipo booleano reconocido por pandas.
    if tipo_esperado_normalizado in {"bool", "boolean"}:
        return is_bool_dtype(serie)

    # Para tipos específicos, comparamos directamente con el dtype de la serie.
    return str(serie.dtype).lower() == tipo_esperado_normalizado

# Función principal para validar que los tipos de datos
# de las columnas coincidan con los tipos esperados definidos en tipos_esperados,


def validar_tipos_esperados(
    df: pd.DataFrame,
    tipos_esperados: dict[str, str] | None,
) -> dict[str, dict[str, str]]:
    """
    Devuelve un diccionario con problemas de tipos detectados.

    Formato:
    {
        "anio": {
            "esperado": "numeric",
            "actual": "object"
        }
    }
    """

    # Si no se pasa ningún tipo esperado, devolvemos un diccionario vacío para evitar invalidar el esquema por falta de referencia.
    if not tipos_esperados:
        return {}

    # Normalizamos las claves del diccionario de tipos esperados para asegurarnos
    # de que coincidan con la normalización aplicada a los nombres de columnas,
    # lo cual es crucial para que la validación funcione correctamente y
    # no reporte falsos positivos por diferencias de formato en los nombres de columnas.
    tipos_esperados_normalizados = _normalizar_tipos_esperados(tipos_esperados)

    # Diccionario para rastrear problemas de tipos detectados, donde cada clave es el nombre de la columna con un problema,
    # y el valor es otro diccionario con el tipo esperado y el tipo actual detectado en el DataFrame,
    # lo cual proporciona información detallada para diagnosticar y corregir problemas de tipos en el esquema de datos.
    problemas_tipos: dict[str, dict[str, str]] = {}

    # Iteramos sobre cada columna y su tipo esperado para validar el tipo de datos de la columna en el DataFrame
    for nombre_columna, tipo_esperado in tipos_esperados_normalizados.items():
        # Si la columna esperada no existe en el DataFrame,
        # no podemos validar su tipo, así que simplemente continuamos con la siguiente columna.
        if nombre_columna not in df.columns:
            continue

        # Obtenemos el tipo actual de la columna en el DataFrame
        # como una cadena para reportar en caso de que no coincida con el tipo esperado.
        tipo_actual = str(df[nombre_columna].dtype)

        # Utilizamos la función _tipo_coincide para evaluar si el tipo de la columna coincide con el tipo esperado,
        # lo cual permite una validación más flexible y práctica,
        # ya que puede manejar tanto tipos prácticos como tipos
        # específicos sin requerir que el usuario especifique cada variante de tipo.
        if not _tipo_coincide(df[nombre_columna], tipo_esperado):
            problemas_tipos[nombre_columna] = {
                "esperado": tipo_esperado,
                "actual": tipo_actual,
            }

    return problemas_tipos

# Función para detectar columnas que no pertenecen al conjunto conocido del esquema,
# el cual se construye a partir de las columnas obligatorias, las claves canónicas de mapa_alias
# y las claves de tipos_esperados, lo cual ayuda a identificar columnas inesperadas que
# podrían indicar problemas de datos o esquema, especialmente cuando permitir_columnas_extra
# es False en la validación del esquema. Si no se pasa ninguna referencia de esquema,
# devuelve una lista vacía para evitar invalidar el esquema por falta de referencia.


def detectar_columnas_inesperadas(
    df: pd.DataFrame,
    columnas_obligatorias: list[str] | None = None,
    mapa_alias: dict[str, list[str]] | None = None,
    tipos_esperados: dict[str, str] | None = None,
) -> list[str]:
    """
    Detecta columnas que no pertenecen al conjunto conocido del esquema.

    El conjunto conocido se construye a partir de:
    - columnas_obligatorias
    - claves canónicas de mapa_alias
    - claves de tipos_esperados

    Si no se pasa ninguna referencia de esquema, devuelve lista vacía.
    """

    # Construimos un conjunto de nombres de columnas conocidos a partir de las columnas obligatorias
    columnas_conocidas: set[str] = set()

    # Agregamos las columnas obligatorias al conjunto de columnas conocidas,
    # normalizando sus nombres para asegurar consistencia con los nombres de columnas del DataFrame.
    if columnas_obligatorias:
        columnas_conocidas.update(normalizar_texto(nombre_columna)
                                  for nombre_columna in columnas_obligatorias)

    # Si se pasan columnas obligatorias, asumimos que el esquema está definido
    # y no reportamos columnas inesperadas para evitar invalidar el esquema por falta de referencia,
    # ya que la validación se basará en las columnas obligatorias como referencia principal
    # para determinar qué columnas son esperadas.
    if mapa_alias:
        columnas_conocidas.update(_normalizar_mapa_alias(mapa_alias).keys())

    # Si se pasa un mapa_alias, asumimos que el esquema está definido y
    # no reportamos columnas inesperadas para evitar invalidar el esquema por falta de referencia,
    # ya que la validación se basará en las claves canónicas del mapa_alias
    # como referencia principal para determinar qué columnas son esperadas.
    if tipos_esperados:
        columnas_conocidas.update(
            _normalizar_tipos_esperados(tipos_esperados).keys())

    # Si se pasan tipos esperados, asumimos que el esquema está definido
    # y no reportamos columnas inesperadas para evitar invalidar el esquema por falta de referencia,
    # ya que la validación se basará en las claves de tipos_esperados
    # como referencia principal para determinar qué columnas son esperadas.
    if not columnas_conocidas:
        return []

    # Detectamos columnas inesperadas comparando los nombres de columnas del DataFrame con el conjunto de columnas conocidas,
    # lo cual ayuda a identificar columnas que no pertenecen al esquema definido
    # por las referencias proporcionadas, y que podrían indicar problemas de datos
    # o esquema, especialmente cuando permitir_columnas_extra es False en la validación del esquema.
    return [nombre_columna for nombre_columna in df.columns if nombre_columna not in columnas_conocidas]


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
def validar_esquema(
    df: pd.DataFrame,
    columnas_obligatorias: list[str] | None = None,
    mapa_alias: dict[str, list[str]] | None = None,
    tipos_esperados: dict[str, str] | None = None,
    permitir_columnas_extra: bool = True,
) -> ResultadoValidacionEsquema:
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
    columnas_obligatorias : list[str] | None
        Lista de columnas obligatorias.
    mapa_alias : dict[str, list[str]] | None
        Mapa de alias por nombre canónico.
    tipos_esperados : dict[str, str] | None
        Tipos esperados por columna.
    permitir_columnas_extra : bool
        Si es False, columnas inesperadas invalidan el esquema.

    Devuelve
    --------
    dict
        Resultado estructurado de la validación.
    """
    columnas_originales = list(df.columns)

    # Normalizamos las columnas del DataFrame para trabajar con nombres consistentes en todas las validaciones posteriores.
    df_trabajo = normalizar_nombres_columnas(df)

    # Detectamos columnas duplicadas después de la normalización,
    # lo cual puede indicar problemas de esquema o datos que deben ser corregidos para garantizar la validez del esquema.
    columnas_duplicadas = detectar_columnas_duplicadas(df_trabajo)

    # Resolvemos columnas alias al nombre canónico definido en mapa_alias,
    # aplicando reglas para evitar conflictos y reportar problemas de alias.
    df_trabajo, columnas_renombradas, conflictos_alias = resolver_alias_columnas(
        df_trabajo,
        mapa_alias=mapa_alias,
    )

    # Validamos que todas las columnas obligatorias estén presentes en el DataFrame,
    # devolviendo una lista de las columnas faltantes para reportar en el resultado de validación del esquema.
    columnas_faltantes = validar_columnas_obligatorias(
        df_trabajo,
        columnas_obligatorias=columnas_obligatorias,
    )

    # Validamos que los tipos de datos de las columnas coincidan con los tipos esperados definidos en tipos_esperados,
    # utilizando funciones de detección de tipos de pandas para una validación más flexible y práctica,
    # y devolviendo un diccionario con problemas de tipos detectados.
    problemas_tipos = validar_tipos_esperados(
        df_trabajo,
        tipos_esperados=tipos_esperados,
    )

    # Detectamos columnas que no pertenecen al conjunto conocido del esquema.
    columnas_inesperadas = detectar_columnas_inesperadas(
        df_trabajo,
        columnas_obligatorias=columnas_obligatorias,
        mapa_alias=mapa_alias,
        tipos_esperados=tipos_esperados,
    )

    # Determinamos si el esquema es válido o no en función de los resultados de las validaciones anteriores,
    # aplicando la lógica de validación que considera el esquema como válido solo si no hay
    # columnas obligatorias faltantes, no hay problemas de tipos, no hay columnas duplicadas,
    # no hay conflictos de alias, y si permitir_columnas_extra es False, no hay columnas inesperadas,
    # lo cual garantiza que el esquema cumple con las expectativas definidas por las referencias proporcionadas
    # y que no contiene problemas que podrían afectar la calidad o integridad de los datos.
    es_valido = (
        len(columnas_faltantes) == 0
        and len(problemas_tipos) == 0
        and len(columnas_duplicadas) == 0
        and len(conflictos_alias) == 0
        and (permitir_columnas_extra or len(columnas_inesperadas) == 0)
    )

    # Devolvemos un resultado estructurado con toda la información relevante sobre la validación del esquema,
    # lo cual proporciona una visión completa del estado del esquema del DataFrame
    # y facilita la identificación y corrección de problemas en los datos.
    return {
        "es_valido": es_valido,
        "datos": df_trabajo,
        "columnas_originales": columnas_originales,
        "columnas": list(df_trabajo.columns),
        "columnas_faltantes": columnas_faltantes,
        "columnas_inesperadas": columnas_inesperadas,
        "columnas_duplicadas": columnas_duplicadas,
        "problemas_tipos": problemas_tipos,
        "columnas_renombradas": columnas_renombradas,
        "conflictos_alias": conflictos_alias,
    }