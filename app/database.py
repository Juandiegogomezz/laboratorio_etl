from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pymongo import MongoClient

from app import config

# ---- MySQL ----
engine = create_engine(config.MYSQL_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ---- MongoDB ----
_mongo_client = MongoClient(config.MONGO_URI)
_mongo_db = _mongo_client[config.MONGO_DB]


def get_mongo_collection():
    """Devuelve la colección personajes_raw de MongoDB."""
    return _mongo_db[config.MONGO_COLLECTION]