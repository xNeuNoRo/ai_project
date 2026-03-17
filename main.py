# Importamos la función de anotaciones futuras para permitir el uso de
# tipos de datos más avanzados y evitar problemas de importación circular en Python 3.7+.
from __future__ import annotations

# Importamos pandas para operaciones tabulares básicas.
import pandas as pd

# Importamos utilidades de configuración y rutas del proyecto.
from src.config import (
    asegurar_estructura_proyecto,
    obtener_ruta_salida,
)

# Importamos utilidades de entrada/salida y preparación base del dataset.
from src.io import cargar_y_preparar_dataset, guardar_dataset

# Importamos la nueva capa de validación, perfilado, análisis,
# indicadores, gráficos y reportes.
from src.validation import validar_esquema
from src.profiling import perfilar_dataset
from src.analysis import (
    resumir_por_grupo,
    resumir_serie_temporal,
    comparar_periodos,
    construir_tabla_pivote,
    obtener_top_n,
)
from src.indicators import (
    calcular_crecimiento,
    calcular_participacion,
    ranking_cambios,
    construir_tabla_indicadores,
    detectar_huecos_temporales,
)
from src.plots import (
    graficar_serie_temporal,
    graficar_barras_top_n,
    graficar_heatmap,
    guardar_figura,
)
from src.reports import (
    exportar_tabla_csv,
    exportar_tablas_excel,
    construir_reporte_markdown,
    escribir_reporte_markdown,
)


# ==========================================================
# Configuración específica del pipeline principal
# ==========================================================

# Nombre lógico del dataset a utilizar.
NOMBRE_DATASET = "Estadisticas-egresados-2009-2025"

# Configuración del esquema esperado para el dataset actual.
COLUMNAS_OBLIGATORIAS = [
    "carrera",
    "masculino",
    "femenino",
    "mes_graduacion",
    "ano_graduacion",
]

MAPA_ALIAS = {
    "carrera": [
        "programa",
    ],
    "masculino": [
        "hombres",
        "varones",
    ],
    "femenino": [
        "mujeres",
    ],
    "mes_graduacion": [
        "mes_de_graduacion",
        "mes",
    ],
    "ano_graduacion": [
        "año_de_graduacion",
        "anio_de_graduacion",
        "ao_de_graduacion",
        "ano",
        "anio",
        "year",
    ],
}

TIPOS_ESPERADOS = {
    "carrera": "string",
    "masculino": "numeric",
    "femenino": "numeric",
    "mes_graduacion": "string",
    "ano_graduacion": "numeric",
}


# ==========================================================
# Funciones auxiliares del pipeline
# ==========================================================

# Función para añadir columnas derivadas útiles para el análisis del dataset actual.
def agregar_columnas_derivadas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega columnas derivadas útiles para análisis de egresados.
    """
    df_trabajo = df.copy()

    df_trabajo["total_egresados"] = (
        df_trabajo["masculino"] + df_trabajo["femenino"]
    )

    df_trabajo["porcentaje_femenino"] = (
        df_trabajo["femenino"] / df_trabajo["total_egresados"].replace(0, pd.NA)
    ) * 100

    df_trabajo["porcentaje_masculino"] = (
        df_trabajo["masculino"] / df_trabajo["total_egresados"].replace(0, pd.NA)
    ) * 100

    df_trabajo["brecha_genero"] = df_trabajo["femenino"] - df_trabajo["masculino"]

    return df_trabajo


# Función para convertir la serie de valores nulos del perfilado en una tabla exportable.
def construir_tabla_valores_nulos(perfil: dict) -> pd.DataFrame:
    """
    Convierte la serie de valores nulos en un DataFrame exportable.
    """
    return (
        perfil["valores_nulos"]
        .rename("cantidad_nulos")
        .reset_index()
        .rename(columns={"index": "columna"})
    )


# Función para construir una tabla simple con el resumen del perfil general.
def construir_tabla_resumen_perfil(perfil: dict) -> pd.DataFrame:
    """
    Construye una tabla simple con métricas generales del perfil del dataset.
    """
    rango_temporal = perfil["rango_temporal"] or {}

    return pd.DataFrame(
        [
            {"metrica": "filas", "valor": perfil["forma"][0]},
            {"metrica": "columnas", "valor": perfil["forma"][1]},
            {"metrica": "total_nulos", "valor": perfil["total_nulos"]},
            {"metrica": "filas_duplicadas", "valor": perfil["filas_duplicadas"]},
            {"metrica": "periodo_minimo", "valor": rango_temporal.get("minimo")},
            {"metrica": "periodo_maximo", "valor": rango_temporal.get("maximo")},
            {"metrica": "periodos_unicos", "valor": rango_temporal.get("periodos_unicos")},
        ]
    )


# Función para construir un mensaje claro si la validación falla.
def construir_mensaje_validacion(resultado_validacion: dict) -> str:
    """
    Construye un mensaje legible a partir del resultado de validación.
    """
    partes: list[str] = ["El esquema del dataset no es válido."]

    if resultado_validacion["columnas_faltantes"]:
        partes.append(
            f"- Columnas faltantes: {resultado_validacion['columnas_faltantes']}"
        )

    if resultado_validacion["columnas_duplicadas"]:
        partes.append(
            f"- Columnas duplicadas: {resultado_validacion['columnas_duplicadas']}"
        )

    if resultado_validacion["problemas_tipos"]:
        partes.append(
            f"- Problemas de tipos: {resultado_validacion['problemas_tipos']}"
        )

    if resultado_validacion["conflictos_alias"]:
        partes.append(
            f"- Conflictos de alias: {resultado_validacion['conflictos_alias']}"
        )

    return "\n".join(partes)


# ==========================================================
# Pipeline principal
# ==========================================================

def main() -> None:
    """
    Ejecuta el pipeline principal de análisis para el dataset actual.
    """
    # Aseguramos la estructura base del proyecto.
    asegurar_estructura_proyecto()

    # Cargamos y preparamos el dataset base.
    df = cargar_y_preparar_dataset(
        nombre_dataset=NOMBRE_DATASET,
        etapa="raw",
        extension="csv",
    )

    # Validamos esquema y normalizamos columnas.
    resultado_validacion = validar_esquema(
        df,
        columnas_obligatorias=COLUMNAS_OBLIGATORIAS,
        mapa_alias=MAPA_ALIAS,
        tipos_esperados=TIPOS_ESPERADOS,
        permitir_columnas_extra=True,
    )

    if not resultado_validacion["es_valido"]:
        raise ValueError(construir_mensaje_validacion(resultado_validacion))

    # Tomamos el DataFrame validado y agregamos columnas derivadas útiles.
    df_trabajo = agregar_columnas_derivadas(resultado_validacion["datos"])

    # Guardamos una versión procesada del dataset ya validado y enriquecido.
    guardar_dataset(
        df_trabajo,
        nombre_dataset=f"{NOMBRE_DATASET}_clean",
        etapa="processed",
        extension="csv",
    )

    # Generamos perfil general del dataset.
    perfil = perfilar_dataset(
        df_trabajo,
        columna_temporal="ano_graduacion",
    )

    # ======================================================
    # Tablas de análisis
    # ======================================================

    resumen_por_carrera = resumir_por_grupo(
        df_trabajo,
        columnas_grupo="carrera",
        columna_valor="total_egresados",
        agregacion="sum",
    )

    resumen_por_mes = resumir_por_grupo(
        df_trabajo,
        columnas_grupo="mes_graduacion",
        columna_valor="total_egresados",
        agregacion="sum",
    )

    serie_anual = resumir_serie_temporal(
        df_trabajo,
        columna_periodo="ano_graduacion",
        columna_valor="total_egresados",
        agregacion="sum",
    )

    crecimiento_anual = calcular_crecimiento(
        df_trabajo,
        columna_periodo="ano_graduacion",
        columna_valor="total_egresados",
    )

    participacion_por_carrera = calcular_participacion(
        df_trabajo,
        columnas_grupo=["ano_graduacion", "carrera"],
        columna_valor="total_egresados",
        dentro_de="ano_graduacion",
    )

    indicadores_por_carrera = construir_tabla_indicadores(
        df_trabajo,
        columnas_grupo="carrera",
        columna_valor="total_egresados",
    )

    huecos_temporales = detectar_huecos_temporales(
        df_trabajo,
        columna_periodo="ano_graduacion",
        columnas_grupo="carrera",
    )

    # Determinamos periodos extremos para comparar evolución.
    periodo_inicial = int(df_trabajo["ano_graduacion"].min())
    periodo_final = int(df_trabajo["ano_graduacion"].max())

    comparacion_periodos = comparar_periodos(
        df_trabajo,
        columna_periodo="ano_graduacion",
        columna_grupo="carrera",
        columna_valor="total_egresados",
        periodo_inicial=periodo_inicial,
        periodo_final=periodo_final,
    )

    ranking_mayores_cambios = ranking_cambios(
        df_trabajo,
        columna_periodo="ano_graduacion",
        columna_grupo="carrera",
        columna_valor="total_egresados",
        periodo_inicial=periodo_inicial,
        periodo_final=periodo_final,
        top_n=10,
    )

    top_carreras = obtener_top_n(
        resumen_por_carrera,
        columna_valor="sum_total_egresados",
        n=10,
        ascendente=False,
    )

    tabla_pivote_carrera = construir_tabla_pivote(
        df_trabajo,
        indice="ano_graduacion",
        columnas="carrera",
        columna_valor="total_egresados",
        agregacion="sum",
    )

    # ======================================================
    # Gráficos
    # ======================================================

    fig_serie, _ = graficar_serie_temporal(
        serie_anual,
        columna_x="ano_graduacion",
        columna_y="sum_total_egresados",
        titulo="Egresados por año",
        etiqueta_x="Año de graduación",
        etiqueta_y="Total de egresados",
    )

    fig_top, _ = graficar_barras_top_n(
        top_carreras,
        columna_categoria="carrera",
        columna_valor="sum_total_egresados",
        top_n=10,
        titulo="Top 10 carreras por total de egresados",
        etiqueta_x="Carrera",
        etiqueta_y="Total de egresados",
    )

    fig_heatmap, _ = graficar_heatmap(
        tabla_pivote_carrera,
        columna_indice="ano_graduacion",
        titulo="Heatmap de egresados por año y carrera",
        etiqueta_x="Carrera",
        etiqueta_y="Año de graduación",
    )

    ruta_figura_serie = obtener_ruta_salida(
        "egresados_por_anio",
        tipo="graficos",
    )
    ruta_figura_top = obtener_ruta_salida(
        "top_carreras_egresados",
        tipo="graficos",
    )
    ruta_figura_heatmap = obtener_ruta_salida(
        "heatmap_egresados_carrera",
        tipo="graficos",
    )

    guardar_figura(fig_serie, ruta_figura_serie)
    guardar_figura(fig_top, ruta_figura_top)
    guardar_figura(fig_heatmap, ruta_figura_heatmap)

    # ======================================================
    # Exportación de tablas
    # ======================================================

    tabla_resumen_perfil = construir_tabla_resumen_perfil(perfil)
    tabla_nulos = construir_tabla_valores_nulos(perfil)

    exportar_tabla_csv(
        serie_anual,
        obtener_ruta_salida("serie_anual_egresados", tipo="tablas"),
    )

    exportar_tablas_excel(
        tablas={
            "perfil_resumen": tabla_resumen_perfil,
            "perfil_nulos": tabla_nulos,
            "resumen_carrera": resumen_por_carrera,
            "resumen_mes": resumen_por_mes,
            "serie_anual": serie_anual,
            "crecimiento_anual": crecimiento_anual,
            "participacion_carrera": participacion_por_carrera,
            "indicadores_carrera": indicadores_por_carrera,
            "huecos_temporales": huecos_temporales,
            "comparacion_periodos": comparacion_periodos["tabla"],
            "ranking_cambios": ranking_mayores_cambios,
        },
        ruta_salida=obtener_ruta_salida(
            "reporte_egresados",
            tipo="tablas",
            extension="xlsx",
        ),
    )

    # ======================================================
    # Reporte Markdown
    # ======================================================

    contenido_markdown = construir_reporte_markdown(
        secciones={
            "Resumen del perfil": tabla_resumen_perfil,
            "Valores nulos por columna": tabla_nulos,
            "Resumen por carrera": resumen_por_carrera,
            "Resumen por mes de graduación": resumen_por_mes,
            "Serie anual": serie_anual,
            "Crecimiento anual": crecimiento_anual,
            "Top carreras": top_carreras,
            "Huecos temporales": huecos_temporales,
            "Comparación entre periodos": comparacion_periodos["tabla"],
            "Ranking de cambios": ranking_mayores_cambios,
        },
        titulo_general="Reporte de egresados",
    )

    escribir_reporte_markdown(
        contenido=contenido_markdown,
        ruta_salida=obtener_ruta_salida("reporte_egresados", tipo="reportes"),
    )

    # ======================================================
    # Resumen final en consola
    # ======================================================

    print("Pipeline ejecutado correctamente.")
    print(f"Dataset analizado: {NOMBRE_DATASET}")
    print(f"Periodo analizado: {periodo_inicial} - {periodo_final}")
    print(f"Filas analizadas: {df_trabajo.shape[0]}")
    print(f"Columnas analizadas: {df_trabajo.shape[1]}")
    print(f"Gráficos guardados en: {obtener_ruta_salida('dummy', tipo='graficos').parent}")
    print(f"Tablas guardadas en: {obtener_ruta_salida('dummy', tipo='tablas').parent}")
    print(f"Reportes guardados en: {obtener_ruta_salida('dummy', tipo='reportes').parent}")


if __name__ == "__main__":
    main()