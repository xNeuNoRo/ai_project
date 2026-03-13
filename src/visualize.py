# Importamos matplotlib para visualización y la ruta del directorio de gráficos GRAFICOS_DIR
from typing import Any
from matplotlib.figure import Figure
from src.config import GRAFICOS_DIR
import pandas as pd


def bar_chart_counts(df: pd.DataFrame, column_name: str, file_name: str) -> None:
    # Verificamos si la columna existe en el DataFrame antes de intentar graficar
    if column_name not in df.columns:
        print(f"Error: La columna '{column_name}' no existe en el DataFrame.")
        return
    # Obtenemos la cantidad de registros por cada valor único en la columna especificada utilizando value_counts()
    counts = df[column_name].value_counts()
    # Creamos una figura tipada con tamaño de 10x6 para evitar errores de tipado con pyplot
    fig = Figure(figsize=(10, 6))
    ax: Any = fig.add_subplot(111)
    # counts.plot(kind="bar") crea un gráfico de barras a partir de las cantidades obtenidas con value_counts()
    counts.plot(kind="bar", ax=ax)
    # Agregamos título y etiquetas a los ejes para mejorar la legibilidad del gráfico
    ax.set_title(f"Cantidad por {column_name}") # Título del gráfico que indica qué se está mostrando
    ax.set_xlabel(column_name) # Etiqueta del eje x que indica la categoría o valor único de la columna
    ax.set_ylabel("Cantidad") # Etiqueta del eje y que indica la cantidad de registros para cada categoría
    # Ajustamos el diseño para evitar que las etiquetas se sobrepongan unas con otras y guardamos el gráfico en la ruta especificada por GRAFICOS_DIR con el nombre de archivo proporcionado
    fig.tight_layout()
    fig.savefig(GRAFICOS_DIR / file_name) # type: ignore