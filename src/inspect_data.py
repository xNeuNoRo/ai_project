def inspect_dataset(df):
    print("\n--- HEADERS DEL DATASET ---")
    # Muestra las primeras filas del DataFrame 
    # para tener una vista previa de los datos
    print(df.head())
    print("\n--- INFORMACIÓN DEL DATASET ---")
    # Muestra información general del DataFrame:
    # numeros de filas, columnas, tipos de datos, valores no nulos, etc.
    print(df.info())
    print("\n--- DIMENSIONES DEL DATASET ---")
    # df.shape devuelve tupla (filas, columnas) del DataFrame
    # Imprimimos el número de filas y columnas para entender la escala del dataset
    print(df.shape)
    print("\n--- NOMBRES DE LAS COLUMNAS ---")
    # Convierte los nombres de columnas a una lista 
    # y la imprime para facilitar su lectura
    print(df.columns.tolist())
    print("\n--- VALORES NULOS POR COLUMNA ---")
    # df.isnull().sum() devuelve el número de valores nulos por cada columna
    # Imprimimos esta información para identificar posibles 
    # problemas de datos faltantes
    print(df.isnull().sum())
    print("\n--- TIPOS DE DATOS POR COLUMNA ---")
    # df.dtypes muestra el tipo de dato de cada columna
    # Esto es útil para entender qué tipo de datos estamos manejando
    print(df.dtypes)