from fastapi import APIRouter, HTTPException
from app.services.perfil_dual_service import obtener_perfil_dual
from app.views.schemas import PerfilDualResponse

router = APIRouter()

@router.get("/analitica/perfil/{id}", response_model=PerfilDualResponse, tags=["Analitica"])
def perfil_dual(id: str):
    """
    Retorna el perfil dual de un personaje consultando MongoDB y MySQL.

    - **200**: Personaje encontrado en una o ambas bases de datos.
    - **404**: Personaje no encontrado en ninguna base de datos.

    Escenarios posibles:
    - Existe en ambas BD: retorna vista_mongo y vista_sql.
    - Solo en MongoDB: retorna vista_mongo, vista_sql=null, warning.
    - Solo en MySQL: retorna vista_mongo=null, vista_sql, warning.
    - No existe: retorna 404.
    """
    resultado = obtener_perfil_dual(id)
    if resultado is None:
        raise HTTPException(status_code=404, detail=f"Personaje '{id}' no encontrado en ninguna base de datos")
    return resultado
