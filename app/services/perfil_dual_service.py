from app.database import get_mongo_collection, SessionLocal
from app.models.entidad_sql import PersonajeHP

def consultar_mongo(id: str):
    """Busca un personaje en MongoDB por su _id."""
    collection = get_mongo_collection()
    personaje = collection.find_one({"_id": id})
    if personaje:
        personaje["_id"] = str(personaje["_id"])
    return personaje

def consultar_mysql(id: str):
    """Busca un personaje en MySQL por su id_personaje."""
    db = SessionLocal()
    try:
        personaje = db.query(PersonajeHP).filter(
            PersonajeHP.id_personaje == id
        ).first()
        if personaje:
            return {
                "id_personaje": personaje.id_personaje,
                "nombre": personaje.nombre,
                "especie": personaje.especie,
                "genero": personaje.genero,
                "casa": personaje.casa,
                "estatus_sangre": personaje.estatus_sangre,
                "nacionalidad": personaje.nacionalidad,
                "estado_civil": personaje.estado_civil,
                "patronus": personaje.patronus,
                "fecha_nacimiento": str(personaje.fecha_nacimiento) if personaje.fecha_nacimiento else None,
                "total_trabajos": personaje.total_trabajos,
                "esta_vivo": personaje.esta_vivo,
            }
        return None
    finally:
        db.close()