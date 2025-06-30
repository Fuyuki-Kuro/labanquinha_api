# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.session import get_database
from app.schemas import user as user_schema
from app.crud import crud_user
from app.api import deps

router = APIRouter()

@router.get("/me", response_model=user_schema.User)
async def read_user_me(current_user: dict = Depends(deps.get_current_user)):
    """
    Retorna os dados do usuário atualmente logado.
    """
    # --- CORREÇÃO EXPLÍCITA ---
    # Forçamos a conversão do _id para string antes de retornar,
    # garantindo que o formato corresponde ao response_model.
    current_user["_id"] = str(current_user["_id"])
    
    return current_user

@router.put("/me", response_model=user_schema.User)
async def update_user_me(
    user_in: user_schema.UserUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Atualiza os dados do usuário atualmente logado.
    """
    user_id = str(current_user["_id"])
    updated_user = await crud_user.update_user(db, user_id=user_id, user_in=user_in)
    
    # Adicionando a mesma conversão explícita aqui para garantir
    # a conformidade da resposta após a atualização.
    if updated_user:
        updated_user["_id"] = str(updated_user["_id"])
        
    return updated_user