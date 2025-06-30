# main.py
from fastapi import FastAPI
from app.db.session import client
from app.api.v1.api import api_router # <--- IMPORTE AQUI

app = FastAPI(
    title="Tabacaria API",
    description="API para o sistema de e-commerce de uma tabacaria.",
    version="1.0.0"
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bem-vindo à API da Tabacaria!"}

# INCLUA O ROTEADOR DA API AQUI
app.include_router(api_router, prefix="/api/v1")