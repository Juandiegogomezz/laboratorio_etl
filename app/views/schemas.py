from pydantic import BaseModel


class TransformacionResponse(BaseModel):
    mensaje: str
    registros_procesados: int
    tabla_destino: str
    status: int