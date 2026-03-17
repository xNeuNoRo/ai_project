# API técnica del proyecto

Este documento describe la API reusable del proyecto para análisis de datasets tabulares, con foco en datasets académicos, históricos e institucionales.

## Objetivo

El proyecto está organizado como una base modular para:

- cargar datasets tabulares,
- validar su esquema,
- perfilar su contenido,
- analizarlos por grupos y periodos,
- calcular indicadores derivados,
- generar gráficos reutilizables,
- exportar tablas y reportes.

`main.py` no se documenta aquí como API porque su función es solo **orquestar** el pipeline principal.

---

# Estructura de módulos documentados

- `src/base/rutas.py`
- `src/config.py`
- `src/io.py`
- `src/validation.py`
- `src/profiling.py`
- `src/analysis.py`
- `src/indicators.py`
- `src/plots.py`
- `src/reports.py`

---

# `src/base/rutas.py`

## Propósito

Este módulo define la estructura física del proyecto en disco.

Su responsabilidad es:

- definir la raíz del proyecto,
- definir los directorios base,
- crear directorios si no existen,
- construir rutas de datasets,
- construir rutas de salida,
- listar la estructura base.

Es la capa más cercana al sistema de archivos.

---

## Constantes públicas

### Raíz y directorios base

- `RAIZ_PROYECTO`
- `DIR_DATA`
- `DIR_DATA_RAW`
- `DIR_DATA_INTERIM`
- `DIR_DATA_PROCESSED`
- `DIR_OUTPUTS`
- `DIR_OUTPUTS_TABLAS`
- `DIR_OUTPUTS_GRAFICOS`
- `DIR_OUTPUTS_REPORTES`
- `DIR_OUTPUTS_MODELOS`
- `DIR_NOTEBOOKS`
- `DIR_TESTS`

Estas constantes exponen rutas absolutas o relativas del proyecto para reutilizarlas desde otros módulos.

---

## Funciones públicas

### `asegurar_directorios() -> None`

Crea la estructura base de carpetas del proyecto si no existe.

#### Qué hace
Se asegura de que existan carpetas como:

- `data/raw`
- `data/interim`
- `data/processed`
- `outputs/tablas`
- `outputs/graficos`
- `outputs/reportes`
- `outputs/modelos`
- `notebooks`
- `tests`

#### Uso esperado
Se llama al inicio del pipeline o antes de guardar resultados.

#### Ejemplo
```python
from src.base.rutas import asegurar_directorios

asegurar_directorios()
```

---

### `obtener_ruta_dataset(nombre_dataset: str, etapa: str = "raw", extension: str = "csv") -> Path`

Construye la ruta esperada de un dataset según:

- nombre lógico,
- etapa del flujo,
- extensión del archivo.

#### Parámetros
- `nombre_dataset`: nombre base del archivo sin extensión
- `etapa`: una de `raw`, `interim`, `processed`
- `extension`: extensión del archivo

#### Retorna
- `Path`

#### Ejemplo
```python
from src.base.rutas import obtener_ruta_dataset

ruta = obtener_ruta_dataset(
    nombre_dataset="egresados_2009_2025",
    etapa="raw",
    extension="csv",
)
```

---

### `obtener_ruta_salida(nombre_archivo: str, tipo: str = "tablas", subcarpeta: str | None = None, extension: str = "csv") -> Path`

Construye una ruta de salida dentro de `outputs`.

#### Tipos esperados
- `tablas`
- `graficos`
- `reportes`
- `modelos`

#### Parámetros
- `nombre_archivo`: nombre base del archivo
- `tipo`: tipo de salida
- `subcarpeta`: subcarpeta opcional dentro del tipo de salida
- `extension`: extensión final del archivo

#### Retorna
- `Path`

#### Ejemplo
```python
from src.base.rutas import obtener_ruta_salida

ruta = obtener_ruta_salida(
    nombre_archivo="reporte_egresados",
    tipo="reportes",
    extension="md",
)
```

---

### `listar_directorios_base() -> dict[str, Path]`

Devuelve un diccionario con los directorios base del proyecto.

#### Uso esperado
Útil para inspección, depuración o documentación programática.

#### Retorna
Diccionario con nombres lógicos y rutas.

---

# `src/config.py`

## Propósito

Este módulo actúa como fachada pública del sistema de configuración.

Su función es:

- exponer nombres y formatos por defecto,
- exponer aliases cómodos de directorios,
- envolver la construcción de rutas,
- servir como punto central de configuración consumido por otros módulos.

Mientras `rutas.py` define la estructura física, `config.py` ofrece una interfaz más cómoda y estable para el resto del proyecto.

---

## Constantes públicas

### Dataset por defecto

- `NOMBRE_DATASET_POR_DEFECTO`
- `EXTENSION_DATASET_POR_DEFECTO`

### Formatos por defecto

- `FORMATO_TABLAS_POR_DEFECTO`
- `FORMATO_GRAFICOS_POR_DEFECTO`
- `FORMATO_REPORTES_POR_DEFECTO`
- `FORMATO_MODELOS_POR_DEFECTO`

### Directorios expuestos

- `DIR_RAIZ_PROYECTO`
- `DIR_DATOS`
- `DIR_DATOS_RAW`
- `DIR_DATOS_INTERIM`
- `DIR_DATOS_PROCESSED`
- `DIR_SALIDAS`
- `DIR_SALIDAS_TABLAS`
- `DIR_SALIDAS_GRAFICOS`
- `DIR_SALIDAS_REPORTES`
- `DIR_SALIDAS_MODELOS`
- `DIR_CUADERNOS`
- `DIR_TESTS_UNITARIOS`

### Rutas por defecto

- `RUTA_DATASET_RAW_POR_DEFECTO`
- `RUTA_DATASET_PROCESSED_POR_DEFECTO`

---

## Funciones públicas

### `asegurar_estructura_proyecto() -> None`

Crea la estructura base de directorios del proyecto si no existe.

#### Uso esperado
Se llama al inicio del pipeline principal.

---

### `obtener_ruta_datos(nombre_dataset: str | None = None, etapa: str = "raw", extension: str | None = None) -> Path`

Devuelve la ruta esperada de un dataset según su nombre, etapa y extensión.

#### Parámetros
- `nombre_dataset`: nombre lógico del dataset; si no se pasa, usa el nombre por defecto
- `etapa`: `raw`, `interim` o `processed`
- `extension`: extensión del archivo; si no se pasa, usa la extensión por defecto

#### Retorna
- `Path`

#### Ejemplo
```python
ruta = obtener_ruta_datos(
    nombre_dataset="Estadisticas-egresados-2009-2025",
    etapa="raw",
    extension="csv",
)
```

---

### `obtener_ruta_salida(nombre_archivo: str, tipo: str = "tablas", subcarpeta: str | None = None, extension: str | None = None) -> Path`

Devuelve una ruta de salida dentro de `outputs`.

#### Parámetros
- `nombre_archivo`
- `tipo`
- `subcarpeta`
- `extension`

#### Comportamiento
Si no se pasa `extension`, asigna una extensión por defecto según el tipo:

- `tablas` → `csv`
- `graficos` → `png`
- `reportes` → `md`
- `modelos` → `joblib`

#### Retorna
- `Path`

---

### `obtener_directorios_base() -> dict[str, Path]`

Devuelve un diccionario con los directorios base del proyecto.

---

# `src/io.py`

## Propósito

Centraliza la entrada y salida de datos del proyecto.

Incluye:

- carga de CSV con fallback de codificación,
- carga general según extensión,
- limpieza básica de texto,
- preparación inicial del dataset,
- guardado de tablas,
- guardado de datasets del proyecto.

Este módulo reemplaza la lógica dispersa de carga y limpieza básica.

---

## Constantes públicas

### `CODIFICACIONES_CSV`

Tupla de codificaciones que se intentan al cargar CSV:

- `utf-8`
- `utf-8-sig`
- `latin1`
- `cp1252`

### `REEMPLAZOS_TEXTO`

Diccionario de reemplazos simples para corregir caracteres problemáticos frecuentes en datasets con codificación inconsistente.

---

## Funciones públicas

### `cargar_csv(ruta_csv: str | Path, **kwargs) -> pd.DataFrame`

Carga un archivo CSV probando varias codificaciones comunes.

#### Parámetros
- `ruta_csv`: ruta al archivo CSV
- `**kwargs`: parámetros adicionales para `pandas.read_csv()`

#### Retorna
- `pd.DataFrame`

#### Ejemplos
```python
df = cargar_csv("data/raw/egresados.csv")
```

```python
df = cargar_csv("data/raw/egresados.csv", sep=";")
```

---

### `cargar_tabla(ruta: str | Path, **kwargs) -> pd.DataFrame`

Carga una tabla según la extensión del archivo.

#### Soporta
- `.csv`
- `.xlsx`
- `.xls`

#### Parámetros
- `ruta`
- `**kwargs`

#### Retorna
- `pd.DataFrame`

---

### `cargar_dataset(nombre_dataset: str, etapa: str = "raw", extension: str = "csv", **kwargs) -> pd.DataFrame`

Carga un dataset del proyecto a partir de su nombre lógico.

#### Parámetros
- `nombre_dataset`
- `etapa`
- `extension`
- `**kwargs`

#### Retorna
- `pd.DataFrame`

#### Ejemplo
```python
df = cargar_dataset(
    nombre_dataset="Estadisticas-egresados-2009-2025",
    etapa="raw",
    extension="csv",
)
```

---

### `limpiar_texto(valor: object) -> object`

Limpia un valor textual aplicando:

- reemplazos básicos de caracteres,
- normalización de espacios,
- `strip()` final.

Si el valor no es string, se devuelve sin cambios.

#### Parámetros
- `valor`

#### Retorna
- `object`

---

### `limpiar_columnas_texto(df: pd.DataFrame, columnas: list[str] | None = None) -> pd.DataFrame`

Limpia columnas de texto de un DataFrame.

#### Comportamiento
- Si `columnas` es `None`, limpia todas las columnas de texto.
- Si se pasa una lista, limpia solo esas columnas que existan.

#### Parámetros
- `df`
- `columnas`

#### Retorna
- `pd.DataFrame`

---

### `preparar_dataset(df: pd.DataFrame, columnas_texto: list[str] | None = None, eliminar_duplicados: bool = True) -> pd.DataFrame`

Aplica una preparación base al dataset.

#### Incluye
- limpieza de texto,
- eliminación opcional de duplicados.

#### Parámetros
- `df`
- `columnas_texto`
- `eliminar_duplicados`

#### Retorna
- `pd.DataFrame`

---

### `cargar_y_preparar_dataset(nombre_dataset: str, etapa: str = "raw", extension: str = "csv", columnas_texto: list[str] | None = None, eliminar_duplicados: bool = True, **kwargs) -> pd.DataFrame`

Carga un dataset y aplica una preparación base en un solo paso.

#### Parámetros
- `nombre_dataset`
- `etapa`
- `extension`
- `columnas_texto`
- `eliminar_duplicados`
- `**kwargs`

#### Retorna
- `pd.DataFrame`

#### Ejemplo
```python
df = cargar_y_preparar_dataset(
    nombre_dataset="Estadisticas-egresados-2009-2025",
    etapa="raw",
    extension="csv",
)
```

---

### `guardar_tabla(tabla: pd.DataFrame, ruta_salida: str | Path, incluir_indice: bool = False, **kwargs) -> Path`

Guarda una tabla según la extensión del archivo.

#### Soporta
- `.csv`
- `.xlsx`
- `.xls`

#### Parámetros
- `tabla`
- `ruta_salida`
- `incluir_indice`
- `**kwargs`

#### Retorna
- `Path`

---

### `guardar_dataset(df: pd.DataFrame, nombre_dataset: str, etapa: str = "processed", extension: str = "csv", incluir_indice: bool = False, **kwargs) -> Path`

Guarda un dataset del proyecto según nombre lógico, etapa y extensión.

#### Parámetros
- `df`
- `nombre_dataset`
- `etapa`
- `extension`
- `incluir_indice`
- `**kwargs`

#### Retorna
- `Path`

---

# `src/validation.py`

## Propósito

Este módulo define la capa de validación del esquema de los datasets.

Su objetivo es:

- normalizar nombres de columnas,
- resolver alias,
- validar columnas obligatorias,
- validar tipos esperados,
- detectar columnas inesperadas,
- devolver un resultado estructurado y reusable.

Es la puerta de entrada formal del pipeline analítico.

---

## Estructuras

### `ResultadoValidacionEsquema`

`TypedDict` que describe la salida estructurada de `validar_esquema()`.

#### Campos
- `es_valido`
- `datos`
- `columnas_originales`
- `columnas`
- `columnas_faltantes`
- `columnas_inesperadas`
- `columnas_duplicadas`
- `problemas_tipos`
- `columnas_renombradas`
- `conflictos_alias`

---

## Funciones públicas

### `normalizar_texto(valor: str) -> str`

Normaliza un texto para usarlo como nombre de columna o clave canónica.

#### Reglas aplicadas
- quita espacios extremos,
- convierte a minúsculas,
- elimina tildes y diacríticos,
- reemplaza separadores por `_`,
- elimina caracteres no alfanuméricos innecesarios,
- colapsa múltiples `_`.

#### Parámetros
- `valor`

#### Retorna
- `str`

#### Ejemplo
```python
normalizar_texto("Año de graduación")
# "ano_de_graduacion"
```

---

### `normalizar_nombres_columnas(df: pd.DataFrame) -> pd.DataFrame`

Devuelve una copia del DataFrame con nombres de columnas normalizados.

#### Parámetros
- `df`

#### Retorna
- `pd.DataFrame`

---

### `detectar_columnas_duplicadas(df: pd.DataFrame) -> list[str]`

Detecta nombres de columnas duplicados.

#### Nota
La detección ocurre sobre el DataFrame ya normalizado, lo que permite descubrir colisiones como:

- `Año`
- `Anio`

si ambos terminan con el mismo nombre lógico.

#### Retorna
- lista de nombres duplicados

---

### `resolver_alias_columnas(df: pd.DataFrame, mapa_alias: dict[str, list[str]] | None) -> tuple[pd.DataFrame, dict[str, str], dict[str, list[str]]]`

Resuelve alias de columnas según un mapa canónico.

#### Qué devuelve
1. `pd.DataFrame` con columnas renombradas
2. diccionario de columnas renombradas
3. diccionario de conflictos de alias

#### Reglas
- si la columna canónica ya existe, no renombra alias adicionales;
- si existen varios alias para la misma canónica y la canónica no existe, renombra solo el primero y reporta el resto como conflicto.

---

### `validar_columnas_obligatorias(df: pd.DataFrame, columnas_obligatorias: list[str] | None) -> list[str]`

Valida que estén presentes todas las columnas obligatorias.

#### Retorna
Lista de columnas faltantes.

---

### `validar_tipos_esperados(df: pd.DataFrame, tipos_esperados: dict[str, str] | None) -> dict[str, dict[str, str]]`

Valida si los tipos de columnas coinciden con lo esperado.

#### Tipos prácticos soportados
- `numeric`
- `string`
- `datetime`
- `bool`

También acepta tipos exactos como:
- `int64`
- `float64`
- `object`
- `category`

#### Retorna
Diccionario con problemas de tipos, por ejemplo:

```python
{
    "ano_graduacion": {
        "esperado": "numeric",
        "actual": "object"
    }
}
```

---

### `detectar_columnas_inesperadas(df: pd.DataFrame, columnas_obligatorias: list[str] | None = None, mapa_alias: dict[str, list[str]] | None = None, tipos_esperados: dict[str, str] | None = None) -> list[str]`

Detecta columnas que no pertenecen al conjunto conocido del esquema.

#### Cómo construye el conjunto conocido
A partir de:
- columnas obligatorias,
- claves canónicas del mapa de alias,
- claves de tipos esperados.

#### Retorna
Lista de columnas inesperadas.

---

### `validar_esquema(df: pd.DataFrame, columnas_obligatorias: list[str] | None = None, mapa_alias: dict[str, list[str]] | None = None, tipos_esperados: dict[str, str] | None = None, permitir_columnas_extra: bool = True) -> ResultadoValidacionEsquema`

Función principal de validación del esquema.

#### Flujo interno
1. normaliza nombres de columnas
2. detecta duplicados
3. resuelve alias
4. valida columnas obligatorias
5. valida tipos esperados
6. detecta columnas inesperadas

#### Parámetros
- `df`
- `columnas_obligatorias`
- `mapa_alias`
- `tipos_esperados`
- `permitir_columnas_extra`

#### Retorna
`ResultadoValidacionEsquema`

#### Ejemplo
```python
resultado = validar_esquema(
    df,
    columnas_obligatorias=["carrera", "ano_graduacion"],
    mapa_alias={
        "ano_graduacion": ["año_de_graduacion", "anio_de_graduacion"],
    },
    tipos_esperados={
        "ano_graduacion": "numeric",
    },
)
```

---

# `src/profiling.py`

## Propósito

Este módulo genera una radiografía general del dataset.

Sirve para conocer:

- forma del DataFrame,
- nombres de columnas,
- tipos de datos,
- nulos,
- duplicados,
- rango temporal,
- valores únicos,
- resúmenes descriptivos.

Es la capa de perfilado automático del dataset.

---

## Estructuras

### `ResultadoPerfiladoDataset`

`TypedDict` con el resultado estructurado de `perfilar_dataset()`.

#### Campos
- `forma`
- `columnas`
- `tipos_datos`
- `valores_nulos`
- `total_nulos`
- `filas_duplicadas`
- `rango_temporal`
- `resumen_valores_unicos`
- `resumen_numerico`
- `resumen_completo`

---

## Funciones públicas

### `resumir_valores_nulos(df: pd.DataFrame) -> pd.Series`

Devuelve la cantidad de valores nulos por columna, ordenada de mayor a menor.

#### Retorna
- `pd.Series`

---

### `contar_filas_duplicadas(df: pd.DataFrame) -> int`

Cuenta filas duplicadas del DataFrame.

#### Retorna
- `int`

---

### `resumir_valores_unicos(df: pd.DataFrame, columnas: list[str] | None = None) -> pd.DataFrame`

Genera un resumen de cantidad de valores únicos por columna.

#### Parámetros
- `df`
- `columnas`: si no se pasa, usa todas las columnas

#### Retorna
`pd.DataFrame` con columnas:
- `columna`
- `valores_unicos`

---

### `obtener_rango_temporal(df: pd.DataFrame, columna_temporal: str | None = None) -> dict[str, object] | None`

Obtiene información básica del rango temporal de una columna.

#### Retorna
- `None` si no se pasa columna o si la columna no existe
- un diccionario con:
  - `columna`
  - `minimo`
  - `maximo`
  - `periodos_unicos`

#### Ejemplo de salida
```python
{
    "columna": "ano_graduacion",
    "minimo": 2009,
    "maximo": 2025,
    "periodos_unicos": 17,
}
```

---

### `perfilar_dataset(df: pd.DataFrame, columna_temporal: str | None = None) -> ResultadoPerfiladoDataset`

Genera el perfil general del dataset.

#### Incluye
- forma
- columnas
- tipos de datos
- valores nulos
- total de nulos
- filas duplicadas
- rango temporal
- resumen de valores únicos
- resumen numérico
- resumen completo

#### Parámetros
- `df`
- `columna_temporal`

#### Retorna
- `ResultadoPerfiladoDataset`

#### Ejemplo
```python
perfil = perfilar_dataset(
    df,
    columna_temporal="ano_graduacion",
)
```

---

# `src/analysis.py`

## Propósito

Este módulo concentra el toolset analítico base del proyecto.

Se encarga de:

- resumir datos por grupos,
- comparar grupos,
- resumir series temporales,
- comparar dos periodos,
- construir pivotes,
- filtrar y seleccionar subconjuntos.

No calcula indicadores derivados avanzados; eso pertenece a `indicators.py`.

---

## Estructuras

### `ResultadoComparacionPeriodos`

`TypedDict` con el resultado estructurado de `comparar_periodos()`.

#### Campos
- `tabla`
- `periodo_inicial`
- `periodo_final`
- `columna_periodo`
- `columna_grupo`
- `columna_valor`

---

## Funciones públicas

### `resumir_por_grupo(df: pd.DataFrame, columnas_grupo: str | list[str], columna_valor: str | None = None, agregacion: str = "count", incluir_nulos: bool = False, ordenar: bool = True, ascendente: bool = False) -> pd.DataFrame`

Resume un DataFrame por una o varias columnas de agrupación.

#### Comportamiento
- Si `columna_valor` es `None`, cuenta registros.
- Si se pasa `columna_valor`, agrega esa columna usando la función indicada.

#### Agregaciones típicas
- `count`
- `sum`
- `mean`
- `median`
- `max`
- `min`

#### Retorna
Tabla resumida.

#### Ejemplos
```python
resumir_por_grupo(df, columnas_grupo="carrera")
```

```python
resumir_por_grupo(
    df,
    columnas_grupo=["ano_graduacion", "carrera"],
    columna_valor="total_egresados",
    agregacion="sum",
)
```

---

### `comparar_grupos(df: pd.DataFrame, columna_grupo: str, columna_valor: str, agregacion: str = "mean", incluir_nulos: bool = False, ordenar: bool = True, ascendente: bool = False) -> pd.DataFrame`

Compara grupos aplicando una agregación sobre una columna objetivo.

#### Esencialmente
Es un wrapper especializado de `resumir_por_grupo()` para el caso común de una sola columna de agrupación.

#### Ejemplo
```python
comparar_grupos(
    df,
    columna_grupo="mes_graduacion",
    columna_valor="total_egresados",
    agregacion="mean",
)
```

---

### `resumir_serie_temporal(df: pd.DataFrame, columna_periodo: str, columna_valor: str | None = None, agregacion: str = "count", columna_grupo: str | None = None, incluir_nulos: bool = False) -> pd.DataFrame`

Resume una serie temporal por periodo.

#### Puede trabajar de dos formas
- solo por periodo,
- por periodo y grupo secundario.

#### Retorna
Tabla ordenada por periodo y, si aplica, por grupo.

#### Ejemplo
```python
resumir_serie_temporal(
    df,
    columna_periodo="ano_graduacion",
    columna_valor="total_egresados",
    agregacion="sum",
)
```

---

### `comparar_periodos(df: pd.DataFrame, columna_periodo: str, columna_grupo: str, columna_valor: str, periodo_inicial: object, periodo_final: object, agregacion: str = "sum") -> ResultadoComparacionPeriodos`

Compara grupos entre dos periodos.

#### Devuelve una tabla con
- `valor_inicial`
- `valor_final`
- `cambio_absoluto`
- `cambio_porcentual`

#### Retorna
`ResultadoComparacionPeriodos`

#### Ejemplo
```python
comparar_periodos(
    df,
    columna_periodo="ano_graduacion",
    columna_grupo="carrera",
    columna_valor="total_egresados",
    periodo_inicial=2009,
    periodo_final=2025,
)
```

---

### `construir_tabla_pivote(df: pd.DataFrame, indice: str | list[str], columnas: str, columna_valor: str, agregacion: str = "sum", rellenar_nulos: object = 0) -> pd.DataFrame`

Construye una tabla pivote reutilizable.

#### Útil para
- análisis por año y categoría,
- preparar barras apiladas,
- preparar heatmaps.

#### Parámetros
- `indice`
- `columnas`
- `columna_valor`
- `agregacion`
- `rellenar_nulos`

#### Retorna
- `pd.DataFrame`

---

### `filtrar_por_periodo(df: pd.DataFrame, columna_periodo: str, periodo_minimo: object | None = None, periodo_maximo: object | None = None) -> pd.DataFrame`

Filtra un DataFrame por rango de periodos.

#### Casos típicos
- 2009–2015
- hasta 2020
- desde 2018

#### Retorna
- `pd.DataFrame`

---

### `filtrar_por_valores(df: pd.DataFrame, columna: str, valores: list[object]) -> pd.DataFrame`

Filtra un DataFrame dejando solo filas cuyo valor en la columna pertenece a la lista indicada.

#### Ejemplo
```python
filtrar_por_valores(
    df,
    columna="carrera",
    valores=["Ingenieria", "Medicina"],
)
```

---

### `obtener_top_n(df: pd.DataFrame, columna_valor: str, n: int = 10, ascendente: bool = False) -> pd.DataFrame`

Devuelve las primeras `N` filas de un DataFrame ordenado por una columna de valor.

#### Uso esperado
Se aplica sobre una tabla ya resumida.

#### Ejemplo
```python
top = obtener_top_n(
    resumen_por_carrera,
    columna_valor="sum_total_egresados",
    n=10,
)
```

---

# `src/indicators.py`

## Propósito

Este módulo calcula indicadores derivados y comparativos construidos sobre tablas o datasets.

Se encarga de:

- crecimiento absoluto y porcentual,
- participación porcentual,
- ranking de cambios,
- detección de huecos temporales,
- tablas de indicadores descriptivos.

Se apoya en `analysis.py` para parte de la lógica base.

---

## Funciones públicas

### `calcular_crecimiento(df: pd.DataFrame, columna_periodo: str, columna_valor: str, columnas_grupo: str | list[str] | None = None, agregacion: str = "sum", incluir_nulos: bool = False) -> pd.DataFrame`

Calcula crecimiento absoluto y porcentual por periodo.

#### Puede trabajar
- globalmente,
- por grupo,
- por múltiples grupos.

#### Devuelve columnas como
- `valor`
- `cambio_absoluto`
- `cambio_porcentual`

#### Ejemplo
```python
crecimiento = calcular_crecimiento(
    df,
    columna_periodo="ano_graduacion",
    columna_valor="total_egresados",
)
```

---

### `calcular_participacion(df: pd.DataFrame, columnas_grupo: str | list[str], columna_valor: str, dentro_de: str | list[str], agregacion: str = "sum", incluir_nulos: bool = False) -> pd.DataFrame`

Calcula la participación porcentual de cada grupo dentro de un total definido por una o varias columnas.

#### Ejemplo típico
Participación de cada carrera dentro de cada año.

#### Devuelve columnas como
- `valor`
- `total_dentro_de`
- `participacion_porcentual`

#### Restricción importante
Las columnas de `dentro_de` deben estar incluidas dentro de `columnas_grupo`.

#### Ejemplo
```python
participacion = calcular_participacion(
    df,
    columnas_grupo=["ano_graduacion", "carrera"],
    columna_valor="total_egresados",
    dentro_de="ano_graduacion",
)
```

---

### `ranking_cambios(df: pd.DataFrame, columna_periodo: str, columna_grupo: str, columna_valor: str, periodo_inicial: object, periodo_final: object, agregacion: str = "sum", criterio_orden: str = "cambio_absoluto", ascendente: bool = False, top_n: int | None = None) -> pd.DataFrame`

Construye un ranking de cambios entre dos periodos.

#### Criterios típicos
- `cambio_absoluto`
- `cambio_porcentual`
- `valor_final`

#### Retorna
Tabla ordenada por el criterio indicado.

#### Ejemplo
```python
ranking = ranking_cambios(
    df,
    columna_periodo="ano_graduacion",
    columna_grupo="carrera",
    columna_valor="total_egresados",
    periodo_inicial=2009,
    periodo_final=2025,
    top_n=10,
)
```

---

### `detectar_huecos_temporales(df: pd.DataFrame, columna_periodo: str, columnas_grupo: str | list[str] | None = None) -> pd.DataFrame`

Detecta periodos faltantes en una serie temporal.

#### Supuesto
La columna de periodo debe ser numérica o convertible a entero.

#### Puede trabajar
- globalmente,
- por grupo,
- por múltiples grupos.

#### Devuelve columnas como
- `columna_periodo`
- `periodo_minimo`
- `periodo_maximo`
- `periodos_esperados`
- `periodos_observados`
- `periodos_faltantes`
- `cantidad_huecos`

#### Ejemplo
```python
huecos = detectar_huecos_temporales(
    df,
    columna_periodo="ano_graduacion",
    columnas_grupo="carrera",
)
```

---

### `construir_tabla_indicadores(df: pd.DataFrame, columnas_grupo: str | list[str], columna_valor: str, incluir_nulos: bool = False) -> pd.DataFrame`

Construye una tabla de indicadores descriptivos por grupo.

#### Incluye
- `total`
- `promedio`
- `mediana`
- `minimo`
- `maximo`
- `desviacion_estandar`
- `registros`

#### Retorna
- `pd.DataFrame`

#### Ejemplo
```python
indicadores = construir_tabla_indicadores(
    df,
    columnas_grupo="carrera",
    columna_valor="total_egresados",
)
```

---

# `src/plots.py`

## Propósito

Este módulo concentra la capa de visualización reusable.

Su filosofía es:

- recibir datos ya preparados,
- generar figuras con matplotlib,
- devolver `fig, ax`,
- guardar solo si se solicita explícitamente.

No hace análisis; solo grafica.

---

## Funciones públicas

### `guardar_figura(fig: plt.Figure, ruta_salida: str | Path, dpi: int = 300, ajustar: bool = True) -> Path`

Guarda una figura en disco.

#### Parámetros
- `fig`
- `ruta_salida`
- `dpi`
- `ajustar`

#### Retorna
- `Path`

#### Ejemplo
```python
guardar_figura(fig, "outputs/graficos/egresados_por_anio.png")
```

---

### `graficar_serie_temporal(df: pd.DataFrame, columna_x: str, columna_y: str, columna_grupo: str | None = None, titulo: str | None = None, etiqueta_x: str | None = None, etiqueta_y: str | None = None, rotacion_x: int = 45, mostrar_leyenda: bool = True, tamano_figura: tuple[int, int] = (10, 6)) -> tuple[plt.Figure, plt.Axes]`

Grafica una serie temporal simple o segmentada por grupo.

#### Casos típicos
- egresados por año
- inscritos por año y carrera
- evolución anual por sede

#### Retorna
- `(fig, ax)`

---

### `graficar_barras(df: pd.DataFrame, columna_x: str, columna_y: str, titulo: str | None = None, etiqueta_x: str | None = None, etiqueta_y: str | None = None, rotacion_x: int = 45, tamano_figura: tuple[int, int] = (10, 6)) -> tuple[plt.Figure, plt.Axes]`

Grafica barras simples a partir de una tabla resumida.

#### Retorna
- `(fig, ax)`

---

### `graficar_barras_top_n(df: pd.DataFrame, columna_categoria: str, columna_valor: str, top_n: int = 10, ascendente: bool = False, titulo: str | None = None, etiqueta_x: str | None = None, etiqueta_y: str | None = None, rotacion_x: int = 45, tamano_figura: tuple[int, int] = (10, 6)) -> tuple[plt.Figure, plt.Axes]`

Grafica barras para las primeras `N` categorías según una columna de valor.

#### Uso típico
- top carreras
- top cambios absolutos
- top participaciones

#### Retorna
- `(fig, ax)`

---

### `graficar_barras_apiladas(df: pd.DataFrame, columna_x: str, columnas_valor: list[str], titulo: str | None = None, etiqueta_x: str | None = None, etiqueta_y: str | None = None, rotacion_x: int = 45, mostrar_leyenda: bool = True, tamano_figura: tuple[int, int] = (11, 6)) -> tuple[plt.Figure, plt.Axes]`

Grafica barras apiladas a partir de una tabla ya pivotada.

#### Uso típico
- composición por carrera dentro de cada año
- composición por sexo dentro de cada periodo

#### Retorna
- `(fig, ax)`

---

### `graficar_heatmap(tabla_pivote: pd.DataFrame, columna_indice: str, titulo: str | None = None, etiqueta_x: str | None = None, etiqueta_y: str | None = None, tamano_figura: tuple[int, int] = (12, 6)) -> tuple[plt.Figure, plt.Axes]`

Grafica un heatmap a partir de una tabla pivote.

#### Uso típico
- año vs carrera
- año vs sede
- periodo vs categoría

#### Retorna
- `(fig, ax)`

---

# `src/reports.py`

## Propósito

Centraliza la salida de tablas y reportes.

Incluye:

- exportación de una tabla a CSV,
- exportación de múltiples tablas a Excel,
- escritura de reportes en TXT,
- escritura de reportes en Markdown,
- conversión de tablas a Markdown,
- construcción de reportes Markdown con varias secciones.

---

## Funciones públicas

### `exportar_tabla_csv(tabla: pd.DataFrame, ruta_salida: str | Path, incluir_indice: bool = False) -> Path`

Exporta una tabla a formato CSV.

#### Parámetros
- `tabla`
- `ruta_salida`
- `incluir_indice`

#### Retorna
- `Path`

---

### `exportar_tablas_excel(tablas: dict[str, pd.DataFrame], ruta_salida: str | Path, incluir_indice: bool = False) -> Path`

Exporta múltiples tablas a un archivo Excel con varias hojas.

#### Comportamiento
- cada clave del diccionario se usa como nombre de hoja,
- los nombres de hoja se recortan a 31 caracteres si hace falta.

#### Parámetros
- `tablas`
- `ruta_salida`
- `incluir_indice`

#### Retorna
- `Path`

#### Ejemplo
```python
exportar_tablas_excel(
    tablas={
        "serie_anual": serie_anual,
        "ranking_cambios": ranking,
    },
    ruta_salida="outputs/tablas/reporte.xlsx",
)
```

---

### `escribir_reporte_txt(contenido: str, ruta_salida: str | Path, encoding: str = "utf-8") -> Path`

Escribe un reporte en texto plano.

#### Retorna
- `Path`

---

### `escribir_reporte_markdown(contenido: str, ruta_salida: str | Path, encoding: str = "utf-8") -> Path`

Escribe un reporte en formato Markdown.

#### Retorna
- `Path`

---

### `tabla_a_markdown(tabla: pd.DataFrame, titulo: str | None = None, incluir_indice: bool = False) -> str`

Convierte una tabla en un bloque Markdown.

#### Comportamiento recomendado
Puede usar `DataFrame.to_markdown()` y, si el entorno no tiene `tabulate`, conviene implementar fallback a texto plano.

#### Retorna
- `str`

#### Ejemplo
```python
bloque = tabla_a_markdown(
    tabla=serie_anual,
    titulo="Serie anual",
)
```

---

### `construir_reporte_markdown(secciones: dict[str, pd.DataFrame], titulo_general: str | None = None, incluir_indice: bool = False) -> str`

Construye un reporte Markdown a partir de varias tablas.

#### Parámetros
- `secciones`: diccionario donde cada clave es el título de una sección y cada valor es una tabla
- `titulo_general`
- `incluir_indice`

#### Retorna
- `str`

#### Ejemplo
```python
contenido = construir_reporte_markdown(
    secciones={
        "Resumen por carrera": resumen_por_carrera,
        "Serie anual": serie_anual,
    },
    titulo_general="Reporte de egresados",
)
```

---

# Relación entre módulos

## Flujo lógico recomendado

### 1. Entrada
- `config.py`
- `base/rutas.py`
- `io.py`

### 2. Validación
- `validation.py`

### 3. Perfilado
- `profiling.py`

### 4. Análisis base
- `analysis.py`

### 5. Indicadores
- `indicators.py`

### 6. Visualización
- `plots.py`

### 7. Exportación
- `reports.py`

---

# Ejemplo mínimo de uso integrado

```python
from src.io import cargar_y_preparar_dataset
from src.validation import validar_esquema
from src.profiling import perfilar_dataset
from src.analysis import resumir_por_grupo
from src.indicators import calcular_crecimiento

df = cargar_y_preparar_dataset(
    nombre_dataset="Estadisticas-egresados-2009-2025",
    etapa="raw",
    extension="csv",
)

resultado_validacion = validar_esquema(
    df,
    columnas_obligatorias=["carrera", "ano_graduacion"],
    mapa_alias={
        "ano_graduacion": ["año_de_graduacion", "anio_de_graduacion"],
    },
    tipos_esperados={
        "ano_graduacion": "numeric",
    },
)

df_valido = resultado_validacion["datos"]

perfil = perfilar_dataset(
    df_valido,
    columna_temporal="ano_graduacion",
)

resumen = resumir_por_grupo(
    df_valido,
    columnas_grupo="carrera",
)

crecimiento = calcular_crecimiento(
    df_valido,
    columna_periodo="ano_graduacion",
    columna_valor="total_egresados",
)
```

---

# Criterios de diseño de esta API

## 1. Modularidad simple
Cada módulo tiene una responsabilidad clara.

## 2. Reutilización
Las funciones devuelven `DataFrame`, `Series`, `dict` o figuras reutilizables.

## 3. Bajo acoplamiento
La lógica no depende rígidamente de un solo dataset.

## 4. Enfoque académico práctico
La arquitectura es lo bastante ordenada para crecer, pero sin sobreingeniería.

## 5. Compatibilidad con Colab
La mayor parte de la lógica vive en módulos `.py`, mientras que los notebooks se enfocan en:

- análisis puntual,
- visualización,
- interpretación,
- experimentación.

---