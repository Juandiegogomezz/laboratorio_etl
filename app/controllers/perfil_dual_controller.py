from fastapi import APIRouter
from app.services.perfil_dual_service import obtener_perfil_dual

router = APIRouter()

@router.get("/analitica/perfil/{id}")
def perfil_dual(id: str):
    return obtener_perfil_dual(id)