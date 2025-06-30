# tests/conftest.py
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient

from app.main import app
from app.core.config import settings
from app.db.session import get_database

@pytest_asyncio.fixture(scope="function")
async def test_db():
    """
    Fixture que cria uma conexão com o banco de dados de teste para uma função de teste.
    """
    # Cria um cliente e DB especificamente para esta função de teste
    test_client = AsyncIOMotorClient(settings.MONGO_URI_TEST)
    db = test_client[settings.DATABASE_NAME_TEST]
    
    yield db  # Fornece a instância do banco de dados para o teste
    
    # --- Teardown ---
    # Limpa o banco de dados e fecha a conexão após o teste terminar
    await test_client.drop_database(settings.DATABASE_NAME_TEST)
    test_client.close()


@pytest_asyncio.fixture(scope="function")
async def client(test_db):
    """
    Fixture que cria um cliente HTTP, usando a fixture do banco de dados de teste.
    """
    # Antes de criar o cliente HTTP, sobrescrevemos a dependência do DB
    # para usar o banco de dados de teste fornecido pela fixture 'test_db'.
    async def override_get_database():
        yield test_db

    app.dependency_overrides[get_database] = override_get_database

    # Cria o cliente HTTP para fazer as requisições
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    # Limpa a sobrescrita da dependência para não afetar outros testes
    app.dependency_overrides.clear()