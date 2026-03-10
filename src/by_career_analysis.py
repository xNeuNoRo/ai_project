def analyze_by_career(df, career_column="carrera"):
    # Verificamos si la columna de carrera existe en el DataFrame
    if career_column not in df.columns:
        # Si la columna no existe, imprimimos un mensaje de error y salimos de la función
        print(f"Error: La columna '{career_column}' no existe en el DataFrame.")
        return
    
    print("\n--- CANTIDAD DE REGISTROS POR CARRERA ---")
    # Imprimimos la cantidad de registros por cada carrera utilizando value_counts()
    print(df[career_column].value_counts())
    
    print("\n--- PORCENTAJE POR CARRERA ---")
    # Imprimimos el porcentaje de registros por cada carrera utilizando 
    # value_counts(normalize=True) multiplicado por 100 para obtener el porcentaje
    # value_counts(normalize=True) devuelve la proporción de cada valor en la columna,
    # multiplicamos por 100 para convertirlo a porcentaje
    print(df[career_column].value_counts(normalize=True) * 100)