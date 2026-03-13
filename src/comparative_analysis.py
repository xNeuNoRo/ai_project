import pandas as pd

def compare_groups(df: pd.DataFrame, group_column: str, target_column: str) -> None:
    # Verificamos si las columnas especificadas existen en el DataFrame antes de realizar el análisis
    if group_column not in df.columns:
        print(f"Error: La columna '{group_column}' no existe en el DataFrame.")
        return

    # Verificamos si la columna objetivo existe en el DataFrame antes de realizar el análisis
    if target_column not in df.columns:
        print(
            f"Error: La columna '{target_column}' no existe en el DataFrame.")
        return

    # Agrupamos el DataFrame por la columna de grupo y calculamos el promedio de la columna objetivo para cada grupo utilizando groupby() y mean()
    # Ej: df.groupby("carrera")["nota_final"].mean() agrupa el DataFrame por la columna "carrera" y calcula el promedio de "nota_final" para cada carrera
    print(f"\n--- PROMEDIO DE {target_column} POR {group_column} ---")
    print(df.groupby(group_column)[target_column].mean())
