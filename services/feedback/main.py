from fastapi import FastAPI
from app.router import router
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Feedback Service", version="1.0.0")

app.include_router(router, prefix="/api/v1")
