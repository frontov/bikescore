from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models.models import Base
from .api import endpoints
from .db import engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="VeloRank API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to VeloRank API"}
