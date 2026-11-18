from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.services.analitica_service import analitica_service
from app.views.schemas import AnalisisColumnaResponse, ErrorColumnaResponse, PerfilDualResponse
from app.services.perfil_dual_service import obtener_perfil_dual

router = APIRouter(prefix="/api/v1/analitica", tags=["Analítica"])

@router.get(
    "/columna/{nombre}",
    response_model=AnalisisColumnaResponse,
    responses={400: {"model": ErrorColumnaResponse}},
)
def analizar_columna(nombre: str):
    try:
        return analitica_service.analizar_columna(nombre)
    except analitica_service.ColumnaNoExisteError as error:
        cuerpo = ErrorColumnaResponse(mensaje=str(error), columnas_validas=error.columnas_validas)
        return JSONResponse(status_code=400, content=cuerpo.model_dump())
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error en el análisis: {error}")

@router.get(
    "/perfil/{id}",
    response_model=PerfilDualResponse,
)
def perfil_dual(id: str):
    """
    Retorna el perfil dual de un personaje consultando MongoDB y MySQL.
    - **200**: Personaje encontrado en una o ambas bases de datos.
    - **404**: Personaje no encontrado en ninguna base de datos.
    """
    resultado = obtener_perfil_dual(id)
    if resultado is None:
        raise HTTPException(status_code=404, detail=f"Personaje '{id}' no encontrado en ninguna base de datos")
    return resultado