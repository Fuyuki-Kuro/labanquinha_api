# app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import settings
from app.db.session import get_database
from app.crud import crud_user
from app.schemas.token import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    # ... (esta função continua exatamente igual) ...
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        phone: str = payload.get("sub")
        if phone is None:
            raise credentials_exception
        token_data = TokenData(phone=phone)
    except (JWTError, ValidationError):
        raise credentials_exception
    
    user = await crud_user.get_user_by_phone(db, phone=token_data.phone)
    if user is None:
        raise credentials_exception
    return user

# --- CRIE A NOVA FUNÇÃO DE DEPENDÊNCIA ABAIXO ---
async def get_current_admin_user(
    current_user: dict = Depends(get_current_user)
):
    """
    Dependência que verifica se o usuário logado tem a permissão de 'admin'.
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: Requer privilégios de administrador."
        )
    return current_user