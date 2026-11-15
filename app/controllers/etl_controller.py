from fastapi import APIRouter, HTTPException

from app.services import etl_service
from app.views.schemas import TransformacionResponse

router = APIRouter(prefix="/api/v1/etl", tags=["ETL"])


@router.post("/transformar", response_model=TransformacionResponse, status_code=200)
def transformar():
    try:
        procesados = etl_service.transformar()
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error en la transformación: {error}")

    if procesados == 0:
        raise HTTPException(
            status_code=404,
            detail="No hay documentos en MongoDB. Ejecuta primero POST /api/v1/etl/extraer",
        )

    return TransformacionResponse(
        mensaje="Pipeline finalizado",
        registros_procesados=procesados,
        tabla_destino="personajes_hp",
        status=200,
    )