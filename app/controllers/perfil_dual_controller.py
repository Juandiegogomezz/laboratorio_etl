from fastapi import APIRouter, HTTPException
from app.services.perfil_dual_service import obtener_perfil_dual
from app.views.schemas import PerfilDualResponse

router = APIRouter()

@router.get("/analitica/perfil/{id}", response_model=PerfilDualResponse)
def perfil_dual(id: str):
    resultado = obtener_perfil_dual(id)
    if resultado is None:
        raise HTTPException(status_code=404, detail=f"Personaje '{id}' no encontrado en ninguna base de datos")
    return resultado
