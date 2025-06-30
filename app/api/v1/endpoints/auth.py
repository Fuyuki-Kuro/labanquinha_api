# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.session import get_database
from app.schemas import user as user_schema
from app.schemas import token as token_schema
from app.crud import crud_user
from app.core import security

router = APIRouter()

@router.post("/register", response_model=user_schema.User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: user_schema.UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Rota para registrar um novo usuário.
    """
    db_user = await crud_user.get_user_by_phone(db, phone=user_in.phone)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Um usuário com este telefone já existe.",
        )
    created_user = await crud_user.create_user(db, user=user_in)
    
    # --- CORREÇÃO EXPLÍCITA ---
    # Convertendo o _id para string antes de retornar a resposta.
    if created_user:
        created_user["_id"] = str(created_user["_id"])
        
    return created_user

@router.post("/token", response_model=token_schema.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Rota de login. O 'username' do formulário será o número de telefone.
    """
    user = await crud_user.get_user_by_phone(db, phone=form_data.username)
    if not user or not security.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telefone ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = security.create_access_token(
        data={"sub": user["phone"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}