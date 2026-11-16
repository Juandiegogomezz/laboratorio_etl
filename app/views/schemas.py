from pydantic import BaseModel, Field

class TransformacionResponse(BaseModel):
    mensaje: str
    registros_procesados: int
    tabla_destino: str
    status: int



class ExtraccionRequest(BaseModel):
    cantidad: int = Field(..., gt=0, description="Cantidad de personajes a extraer, mayor que 0")


class ExtraccionResponse(BaseModel):
    mensaje: str
    nuevos: int
    ya_existentes: int
    fuente: str
    status: int


class ResetResponse(BaseModel):
    mensaje: str
    mongo_docs_eliminados: int
    mysql_rows_eliminadas: int
    status: int


    # ============ Analítica: Endpoint D - Análisis por columna (Yohana) ============
from datetime import date
from typing import Annotated, Literal, Optional, Union


class AnalisisCategorico(BaseModel):
    columna: str
    tipo: Literal["categorica"] = "categorica"
    valores_unicos: int
    distribucion: dict[str, int]
    valor_mas_comun: Optional[str]
    sin_dato: int
    nulos: int


class AnalisisNumerico(BaseModel):
    columna: str
    tipo: Literal["numerica"] = "numerica"
    min: Optional[float]
    max: Optional[float]
    promedio: Optional[float]
    mediana: Optional[float]
    desviacion_std: Optional[float]
    nulos: int


class AnalisisFecha(BaseModel):
    columna: str
    tipo: Literal["fecha"] = "fecha"
    min: Optional[date]
    max: Optional[date]
    rango_dias: Optional[int]
    nulos: int


class AnalisisBooleano(BaseModel):
    columna: str
    tipo: Literal["booleana"] = "booleana"
    true: int
    false: int
    nulos: int


class AnalisisTexto(BaseModel):
    columna: str
    tipo: Literal["texto"] = "texto"
    valores_unicos: int
    nulos: int


AnalisisColumnaResponse = Annotated[
    Union[AnalisisCategorico, AnalisisNumerico, AnalisisFecha, AnalisisBooleano, AnalisisTexto],
    Field(discriminator="tipo"),
]


class ErrorColumnaResponse(BaseModel):
    mensaje: str
    columnas_validas: list[str]