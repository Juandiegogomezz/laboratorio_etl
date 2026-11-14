from sqlalchemy import Column, String, Date, Integer, Boolean

from app.database import Base


class Personaje(Base):
    """Tabla plana con los personajes ya limpios (Data Warehouse)."""

    __tablename__ = "personajes_hp"

    # PK: el mismo id (slug) que se guarda como _id en MongoDB. No es autoincremental.
    id_personaje = Column(String(150), primary_key=True, autoincrement=False)

    # Texto libre
    nombre = Column(String(150), nullable=False)

    # Categóricas (vacíos -> "N/A")
    especie = Column(String(50), nullable=False, default="N/A")
    genero = Column(String(20), nullable=False, default="N/A")
    casa = Column(String(30), nullable=False, default="N/A")
    estatus_sangre = Column(String(50), nullable=False, default="N/A")
    nacionalidad = Column(String(50), nullable=False, default="N/A")
    estado_civil = Column(String(50), nullable=False, default="N/A")
    patronus = Column(String(100), nullable=False, default="N/A")

    # Fecha (vacía o aproximada -> NULL)
    fecha_nacimiento = Column(Date, nullable=True)

    # Derivadas
    total_trabajos = Column(Integer, nullable=True)  # len(jobs)
    esta_vivo = Column(Boolean, nullable=True)       # True si died viene vacío