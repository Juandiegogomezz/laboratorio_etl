import numpy as np
import pandas as pd
from sqlalchemy.dialects.mysql import insert

from app.database import Base, engine, get_mongo_collection
from app.models.entidad_sql import Personaje


# Campo en Mongo (API) -> columna en MySQL
MAPEO_COLUMNAS = {
    "_id": "id_personaje",
    "name": "nombre",
    "species": "especie",
    "gender": "genero",
    "house": "casa",
    "blood_status": "estatus_sangre",
    "nationality": "nacionalidad",
    "marital_status": "estado_civil",
    "patronus": "patronus",
    "born": "fecha_nacimiento",
}

# Columnas categóricas: si vienen vacías se rellenan con "N/A"
COLUMNAS_TEXTO = [
    "especie", "genero", "casa", "estatus_sangre",
    "nacionalidad", "estado_civil", "patronus",
]


def limpiar_datos(documentos: list) -> pd.DataFrame:
    """T (Transform): convierte los documentos crudos de Mongo en una tabla limpia."""
    df = pd.DataFrame(documentos)

    # Si algún campo no vino en ningún documento, se crea vacío para no romper el pipeline
    for campo in list(MAPEO_COLUMNAS) + ["jobs", "died"]:
        if campo not in df.columns:
            df[campo] = None

    # La API marca muchos faltantes como texto vacío "": se convierten a nulo
    df = df.replace("", np.nan)

    # Columnas derivadas (aplanamiento de la lista jobs y del campo died)
    df["total_trabajos"] = df["jobs"].apply(lambda x: len(x) if isinstance(x, list) else 0)
    df["esta_vivo"] = df["died"].isna()

    # Quedarse solo con las columnas útiles y ponerles nombres claros
    df = df[list(MAPEO_COLUMNAS) + ["total_trabajos", "esta_vivo"]]
    df = df.rename(columns=MAPEO_COLUMNAS)

    # Texto: quitar espacios; categóricas vacías -> "N/A"
    df["nombre"] = df["nombre"].astype(str).str.strip()
    for columna in COLUMNAS_TEXTO:
        df[columna] = df[columna].fillna("N/A").astype(str).str.strip()

    # Fecha: "31 July 1980" -> 1980-07-31. Si es aproximada o vacía queda NULL
    df["fecha_nacimiento"] = pd.to_datetime(
        df["fecha_nacimiento"], format="%d %B %Y", errors="coerce"
    ).dt.date

    # Cualquier NaN/NaT que quede se convierte en None (NULL en MySQL)
    df = df.astype(object).where(pd.notna(df), None)
    return df


def transformar() -> int:
    """Lee de Mongo, limpia con Pandas y carga en MySQL sin duplicar. Devuelve cuántos registros procesó."""
    # E: leer todos los documentos crudos
    documentos = list(get_mongo_collection().find())
    if not documentos:
        return 0

    # T: limpiar
    df = limpiar_datos(documentos)
    registros = df.to_dict(orient="records")

    # L: crear la tabla si no existe (conserva la PK) y hacer upsert
    Base.metadata.create_all(bind=engine)
    tabla = Personaje.__table__
    consulta = insert(tabla).values(registros)
    columnas_a_actualizar = {
        col.name: consulta.inserted[col.name]
        for col in tabla.columns
        if col.name != "id_personaje"
    }
    consulta = consulta.on_duplicate_key_update(**columnas_a_actualizar)

    with engine.begin() as conexion:
        conexion.execute(consulta)

    return len(registros)