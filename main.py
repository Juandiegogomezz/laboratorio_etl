from fastapi import FastAPI

from app.database import Base, engine
from app.controllers.etl_controller import router as etl_router

app = FastAPI(title="Lab Final ETL - Hogwarts API")

Base.metadata.create_all(bind=engine)

app.include_router(etl_router)