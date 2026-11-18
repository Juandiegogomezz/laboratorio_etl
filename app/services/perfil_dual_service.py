from app.database import get_mongo_collection

def consultar_mongo(id: str):
    """Busca un personaje en MongoDB por su _id."""
    collection = get_mongo_collection()
    personaje = collection.find_one({"_id": id})
    if personaje:
        personaje["_id"] = str(personaje["_id"])
    return personaje