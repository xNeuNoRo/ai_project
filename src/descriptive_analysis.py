def descriptive_analysis(df):
    print("\n--- ESTADÍSTICAS NUMÉRICAS ---")
    # df.describe() devuelve estadísticas descriptivas para las columnas numéricas del DataFrame
    # Incluye conteo, media, desviación estándar, valores mínimos, percentiles y máximos
    print(df.describe())
    
    print("\n--- ESTADISTICAS COMPLETAS ---")
    # df.describe(include="all") devuelve estadísticas descriptivas para todas las columnas del DataFrame
    # Incluye conteo, valores únicos, valor más frecuente (top), frecuencia del valor más frecuente (freq), además de las estadísticas numéricas para las columnas numéricas
    print(df.describe(include="all"))