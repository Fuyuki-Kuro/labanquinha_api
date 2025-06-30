# app/db/session.py
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

# Cria uma instância do cliente MongoDB
# Esta instância será reutilizada em toda a aplicação (Singleton)
client = AsyncIOMotorClient(settings.MONGO_URI)

# Acessa o banco de dados especificado no .env
database = client[settings.DATABASE_NAME]

# Função para obter a instância do banco de dados (será usada para dependências)
async def get_database():
    return database