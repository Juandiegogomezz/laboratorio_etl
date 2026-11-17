import pandas as pd
from sqlalchemy import Boolean, Date, DateTime, Float, Integer, Numeric, select

from app.database import engine
from app.models.entidad_sql import Personaje

# La tabla se toma del modelo de SQLAlchemy: si el modelo cambia, el análisis se adapta solo
TABLA = Personaje.__table__

# Si al menos este porcentaje de valores es distinto, la columna se trata como texto libre
UMBRAL_TEXTO_LIBRE = 0.9

# Valor con el que la transformación rellena los textos vacíos
VALOR_SIN_DATO = "N/A"


class ColumnaNoExisteError(Exception):
    """Se lanza cuando piden una columna que no está en la tabla."""

    def __init__(self, columna: str, columnas_validas: list[str]):
        self.columnas_validas = columnas_validas
        super().__init__(f"La columna '{columna}' no existe en la tabla {TABLA.name}")


class TablaVaciaError(Exception):
    """Se lanza cuando la tabla SQL no tiene registros."""


def obtener_columnas_validas() -> list[str]:
    """Nombres de todas las columnas de la tabla, leídos del modelo."""
    return [columna.name for columna in TABLA.columns]


def leer_columna(nombre: str) -> pd.Series:
    """Lee una sola columna de MySQL con Pandas. Si es fecha, la convierte a datetime."""
    es_fecha = isinstance(TABLA.columns[nombre].type, (Date, DateTime))
    consulta = select(TABLA.columns[nombre])
    df = pd.read_sql(consulta, engine, parse_dates=[nombre] if es_fecha else None)
    return df[nombre]


def detectar_tipo(nombre: str, serie: pd.Series) -> str:
    """Decide el tipo de análisis según el tipo SQL de la columna (sin nombres fijos)."""
    tipo_sql = TABLA.columns[nombre].type

    if isinstance(tipo_sql, Boolean):
        return "booleana"
    if isinstance(tipo_sql, (Date, DateTime)):
        return "fecha"
    if isinstance(tipo_sql, (Integer, Float, Numeric)):
        return "numerica"

    # Es texto: si casi todos los valores son distintos es texto libre; si se repiten mucho, categórica
    con_valor = serie.dropna()
    if con_valor.empty:
        return "categorica"
    proporcion_unicos = con_valor.nunique() / len(con_valor)
    if proporcion_unicos >= UMBRAL_TEXTO_LIBRE:
        return "texto"
    return "categorica"


def analizar_categorica(nombre: str, serie: pd.Series) -> dict:
    """Distribución de valores sin contar los "N/A", que se reportan aparte como sin_dato."""
    sin_dato = int((serie == VALOR_SIN_DATO).sum())
    con_dato = serie[serie.notna() & (serie != VALOR_SIN_DATO)]
    distribucion = con_dato.value_counts()
    return {
        "columna": nombre,
        "tipo": "categorica",
        "valores_unicos": int(con_dato.nunique()),
        "distribucion": {str(valor): int(cantidad) for valor, cantidad in distribucion.items()},
        "valor_mas_comun": str(distribucion.index[0]) if not distribucion.empty else None,
        "sin_dato": sin_dato,
        "nulos": int(serie.isna().sum()),
    }


def analizar_texto(nombre: str, serie: pd.Series) -> dict:
    """Para texto libre solo tiene sentido contar valores distintos y nulos."""
    return {
        "columna": nombre,
        "tipo": "texto",
        "valores_unicos": int(serie.nunique()),
        "nulos": int(serie.isna().sum()),
    }


# Cada tipo detectado se asocia con la función que lo analiza
ANALIZADORES = {
    "categorica": analizar_categorica,
    "texto": analizar_texto,
}


def analizar_columna(nombre: str) -> dict:
    """Valida la columna, la lee de MySQL, detecta su tipo y aplica el análisis que le corresponde."""
    columnas = obtener_columnas_validas()
    if nombre not in columnas:
        raise ColumnaNoExisteError(nombre, columnas)

    serie = leer_columna(nombre)
    if serie.empty:
        raise TablaVaciaError(
            f"La tabla {TABLA.name} está vacía. Ejecuta primero POST /api/v1/etl/transformar"
        )

    tipo = detectar_tipo(nombre, serie)
    if tipo not in ANALIZADORES:
        raise NotImplementedError(f"Tipo detectado: {tipo}. El análisis de este tipo está en construcción")
    return ANALIZADORES[tipo](nombre, serie)