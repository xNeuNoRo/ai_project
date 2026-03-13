# Importamos la ruta del archivo CLEAN_FILE desde config.py
from src.config import CLEAN_FILE

import pandas as pd

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    # Creamos una copia del DataFrame original para evitar modificarlo directamente
    df = df.copy()
    
    # Limpiamos los nombres de las columnas: eliminamos espacios, convertimos a minúsculas y reemplazamos espacios por guiones bajos
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    
    # Eliminamos filas duplicadas para evitar redundancias en el análisis
    df = df.drop_duplicates()
    
    # Retornamos el DataFrame limpio para su posterior uso o guardado
    return df

def save_clean_dataset(df: pd.DataFrame) -> None:
    # Guardamos el DataFrame limpio en un archivo CSV en la ruta especificada por CLEAN_FILE
    df.to_csv(CLEAN_FILE, index=False) # index=False para no guardar el índice del DataFrame en el CSV