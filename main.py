# Importamos la funcionalidad para cargar el dataset
from src.load_data import load_dataset
# Importamos la funcionalidad para inspeccionar el dataset
from src.inspect_data import inspect_dataset
# Importamos la funcionalidad para limpiar (de manera basica) el dataset
from src.clean_data import clean_dataset, save_clean_dataset
# Importamos la funcionalidad para realizar análisis descriptivo
from src.descriptive_analysis import descriptive_analysis
# Importamos la funcionalidad para realizar análisis por carrera
from src.by_career_analysis import analyze_by_career
# Importamos la funcionalidad para realizar análisis comparativo entre grupos
from src.comparative_analysis import compare_groups
# Importamos la funcionalidad para visualizar datos con gráficos de barras
from src.visualize import bar_chart_counts
# Importamos la funcionalidad para realizar regresión lineal simple
from src.simple_model import simple_linear_regression

def main():
    df = load_dataset()

    inspect_dataset(df)

    df_clean = clean_dataset(df)
    
    
    df_clean["total_estudiantes"] = (
        df_clean["estudiantes_femeninos"] + df_clean["estudiantes_masculinos"]
    )

    df_clean["porcentaje_femenino"] = (
        df_clean["estudiantes_femeninos"] / df_clean["total_estudiantes"]
    ) * 100

    df_clean["porcentaje_masculino"] = (
        df_clean["estudiantes_masculinos"] / df_clean["total_estudiantes"]
    ) * 100

    df_clean["brecha_genero"] = (
        df_clean["estudiantes_femeninos"] - df_clean["estudiantes_masculinos"]
    )

    save_clean_dataset(df_clean)

    descriptive_analysis(df_clean)

    analyze_by_career(df_clean, career_column="carrera")

    compare_groups(df_clean, group_column="cuatrimestre", target_column="total_estudiantes")
    compare_groups(df_clean, group_column="carrera", target_column="porcentaje_femenino")
    
    df_yearly = df_clean.groupby("año", as_index=False)["total_estudiantes"].sum()

    print("\n--- TOTAL DE ESTUDIANTES POR AÑO ---")
    print(df_yearly)

    simple_linear_regression(df_yearly, x_column="año", y_column="total_estudiantes")

if __name__ == "__main__":
    main()