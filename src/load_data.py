# Importamos pandas y la ruta del archivo RAW_FILE
import pandas as pd
from src.config import RAW_FILE

def load_dataset():
    # Cargamos el dataset (CSV) desde la ruta especificada en RAW_FILE
    df = pd.read_csv(RAW_FILE)
    # Devolvemos el DataFrame cargado para su posterior procesamiento
    return df