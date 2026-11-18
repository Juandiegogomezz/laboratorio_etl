from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.services import analitica_service
from app.services.perfil_dual_service import obtener_perfil_dual
from app.views.schemas import AnalisisColumnaResponse, ErrorColumnaResponse, PerfilDualResponse

router = APIRouter(prefix="/api/v1/analitica", tags=["Analítica"])


@router.get(
    "/columna/{nombre}",
    response_model=AnalisisColumnaResponse,
    summary="Análisis estadístico de una columna de la tabla SQL",
    description=(
        "Detecta dinámicamente el tipo de la columna a partir del modelo SQLAlchemy "
        "(categórica, texto, numérica, fecha o booleana) y devuelve el análisis que le corresponde."
    ),
    responses={
        400: {"model": ErrorColumnaResponse, "description": "La columna no existe en la tabla"},
        404: {"description": "La tabla está vacía; primero hay que ejecutar /etl/transformar"},
        500: {"description": "Error inesperado al leer o analizar la columna"},
    },
)
def analizar_columna(nombre: str):
    try:
        return analitica_service.analizar_columna(nombre)
    except analitica_service.ColumnaNoExisteError as error:
        cuerpo = ErrorColumnaResponse(mensaje=str(error), columnas_validas=error.columnas_validas)
        return JSONResponse(status_code=400, content=cuerpo.model_dump())
    except analitica_service.TablaVaciaError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error en el análisis: {error}")


@router.get(
    "/perfil/{id}",
    response_model=PerfilDualResponse,
    summary="Perfil dual: el mismo registro visto en MongoDB y en MySQL",
    responses={404: {"description": "El registro no existe en ninguna de las dos bases"}},
)
def perfil_dual(id: str):
    """
    Retorna el perfil dual de un personaje consultando MongoDB y MySQL.
    - **200**: encontrado en una o ambas bases (si falta en una, incluye un warning).
    - **404**: no encontrado en ninguna base.
    """
    resultado = obtener_perfil_dual(id)
    if resultado is None:
        raise HTTPException(status_code=404, detail=f"Personaje '{id}' no encontrado en ninguna base de datos")
    return resultado
