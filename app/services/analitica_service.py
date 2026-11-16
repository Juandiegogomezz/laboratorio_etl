from app.models.entidad_sql import Personaje

# La tabla se toma del modelo de SQLAlchemy: si el modelo cambia, el análisis se adapta solo
TABLA = Personaje.__table__


class ColumnaNoExisteError(Exception):
    """Se lanza cuando piden una columna que no está en la tabla."""

    def __init__(self, columna: str, columnas_validas: list[str]):
        self.columnas_validas = columnas_validas
        super().__init__(f"La columna '{columna}' no existe en la tabla {TABLA.name}")


def obtener_columnas_validas() -> list[str]:
    """Nombres de todas las columnas de la tabla, leídos del modelo."""
    return [columna.name for columna in TABLA.columns]


def analizar_columna(nombre: str) -> dict:
    """Valida la columna y aplica el análisis que le corresponde según su tipo."""
    columnas = obtener_columnas_validas()
    if nombre not in columnas:
        raise ColumnaNoExisteError(nombre, columnas)

    raise NotImplementedError("El análisis de la columna todavía está en construcción")