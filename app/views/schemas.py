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