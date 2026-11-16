from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError
from sqlalchemy.exc import SQLAlchemyError

from app.services import etl_service
from app.views.schemas import TransformacionResponse, ExtraccionRequest, ExtraccionResponse,ResetResponse

router = APIRouter(prefix="/api/v1/etl", tags=["ETL"])


@router.post("/transformar", response_model=TransformacionResponse, status_code=200)
def transformar():
    try:
        procesados = etl_service.transformar()
    except PyMongoError as error:
        raise HTTPException(status_code=503, detail=f"No se pudo leer MongoDB: {error}")
    except SQLAlchemyError as error:
        raise HTTPException(status_code=500, detail=f"Error al cargar en MySQL: {error}")    
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

@router.post("/extraer", response_model=ExtraccionResponse, status_code=201)
def extraer(payload: ExtraccionRequest):
    try:
        resultado = etl_service.extraer(payload.cantidad)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error en la extracción: {error}")

    return ExtraccionResponse(
        mensaje="Datos extraídos exitosamente",
        nuevos=resultado["nuevos"],
        ya_existentes=resultado["ya_existentes"],
        fuente="Hogwarts API",
        status=201,
    )

@router.delete("/reset", response_model=ResetResponse, status_code=200)
def reset():
    try:
        resultado = etl_service.reset()
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error en el reset: {error}")

    return ResetResponse(
        mensaje="Sistema reseteado correctamente",
        mongo_docs_eliminados=resultado["mongo_docs_eliminados"],
        mysql_rows_eliminadas=resultado["mysql_rows_eliminadas"],
        status=200,
    )