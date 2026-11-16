from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.services import analitica_service
from app.views.schemas import AnalisisColumnaResponse, ErrorColumnaResponse

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