import pandas as pd
from sqlalchemy import Date, DateTime, select

from app.database import engine
from app.models.entidad_sql import Personaje

# La tabla se toma del modelo de SQLAlchemy: si el modelo cambia, el análisis se adapta solo
TABLA = Personaje.__table__


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


def analizar_columna(nombre: str) -> dict:
    """Valida la columna, la lee de MySQL y aplica el análisis que le corresponde según su tipo."""
    columnas = obtener_columnas_validas()
    if nombre not in columnas:
        raise ColumnaNoExisteError(nombre, columnas)

    serie = leer_columna(nombre)
    if serie.empty:
        raise TablaVaciaError(
            f"La tabla {TABLA.name} está vacía. Ejecuta primero POST /api/v1/etl/transformar"
        )

    raise NotImplementedError("El análisis de la columna todavía está en construcción")