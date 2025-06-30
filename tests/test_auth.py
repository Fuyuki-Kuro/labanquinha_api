# tests/test_auth.py
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_register_user_success(client: AsyncClient):
    """
    Testa o registro de um novo usuário com sucesso.
    """
    # Dados do usuário de teste
    test_user = {
        "name": "Test",
        "lastName": "User",
        "phone": "+5531999999999",
        "birthDate": "1990-01-01",
        "cpf": "11122233344",
        "password": "testpassword"
    }

    response = await client.post("/api/v1/auth/register", json=test_user)

    # 1. Verifica se o status code é 201 (Created)
    assert response.status_code == 201

    # 2. Verifica se a resposta contém os dados corretos
    response_data = response.json()
    assert response_data["name"] == test_user["name"]
    assert response_data["phone"] == test_user["phone"]
    
    # 3. Garante que a senha NUNCA é retornada na resposta
    assert "password" not in response_data
    assert "hashed_password" not in response_data