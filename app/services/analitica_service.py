import pandas as pd
from sqlalchemy import Boolean, Date, DateTime, Float, Integer, Numeric, select

from app.database import engine
from app.models.entidad_sql import Personaje

# La tabla se toma del modelo de SQLAlchemy: si el modelo cambia, el análisis se adapta solo
TABLA = Personaje.__table__

# Si al menos este porcentaje de valores es distinto, la columna se trata como texto libre
UMBRAL_TEXTO_LIBRE = 0.9


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
    raise NotImplementedError(f"Tipo detectado: {tipo}. El análisis de este tipo está en construcción")