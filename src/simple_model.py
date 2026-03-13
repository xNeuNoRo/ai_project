import pandas as pd
from sklearn.linear_model import LinearRegression

def simple_linear_regression(df: pd.DataFrame, x_column: str, y_column: str) -> None:
    # Verificamos si las columnas especificadas existen en el DataFrame antes de realizar el análisis
    if x_column not in df.columns:
        print(f"Error: La columna '{x_column}' no existe en el DataFrame.")
        return
    if y_column not in df.columns:
        print(f"Error: La columna '{y_column}' no existe en el DataFrame.")
        return
    
    # Creamos un nuevo DataFrame que solo contenga las columnas de interés (x_column y y_column) y eliminamos filas con valores faltantes utilizando dropna()
    model_df = df[[x_column, y_column]].dropna()
    
    # Con model_df[[x_column]] seleccionamos la columna x_column como una matriz de características (X) y model_df[y_column] seleccionamos la columna y_column como el vector/variable objetivo (Y)
    X = model_df[[x_column]]
    Y = model_df[y_column]
    
    # Creamos una instancia del modelo de regresión lineal utilizando LinearRegression()
    model = LinearRegression()
    
    # Entrenamos el modelo con los datos utilizando el método fit() con X como las características y Y como la variable objetivo
    model.fit(X,Y)
    
    # Imprimimos los resultados del modelo, incluyendo el intercepto, el coeficiente de la variable independiente y el R^2 (coeficiente de determinación) que indica qué tan bien se ajusta el modelo a los datos
    # Estos datos quieren (de forma sencilla) decir lo siguiente:
    # Intercepto: el valor de Y cuando X es 0 (punto donde la línea de regresión cruza el eje Y)
    # Coeficiente: cuánto cambia Y por cada unidad de cambio en X (pendiente de la línea de regresión)
    # R^2: una medida de qué tan bien el modelo explica la variabilidad de los datos 
    # (1 es un ajuste perfecto, 0 significa que el modelo no explica nada de la variabilidad)
    print("\n--- RESULTADOS DEL MODELO ---")
    print("Intercepto:", model.intercept_)
    print("Coeficiente:", model.coef_[0])
    print("R^2:", model.score(X, Y))