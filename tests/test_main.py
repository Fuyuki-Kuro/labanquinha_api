# tests/test_main.py
import pytest
from httpx import AsyncClient

# Marca todos os testes neste arquivo para serem executados com asyncio
pytestmark = pytest.mark.asyncio


async def test_read_root(client: AsyncClient):
    """
    Testa se a rota raiz ("/") retorna a mensagem de boas-vindas.
    """
    response = await client.get("/")
    
    # Verifica se a resposta foi bem-sucedida (status code 200)
    assert response.status_code == 200
    
    # Verifica se o conteúdo da resposta é o esperado
    assert response.json() == {"message": "Bem-vindo à API da Tabacaria!"}