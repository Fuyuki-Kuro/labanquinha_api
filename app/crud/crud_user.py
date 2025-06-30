# app/crud/crud_user.py
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime

from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash

COLLECTION_NAME = "users"

async def get_user_by_phone(db: AsyncIOMotorDatabase, phone: str):
    """
    Busca um usuário no banco de dados pelo seu número de telefone.
    """
    return await db[COLLECTION_NAME].find_one({"phone": phone})

async def create_user(db: AsyncIOMotorDatabase, user: UserCreate):
    """
    Cria um novo usuário no banco de dados.
    - Hashes a senha antes de salvar.
    - Converte o 'birthDate' (date) para um objeto 'datetime' compatível com o MongoDB.
    """
    hashed_password = get_password_hash(user.password)
    
    user_data = user.model_dump(exclude={"password"})
    user_data["hashed_password"] = hashed_password
    user_data["addresses"] = []
    
    if user_data.get("birthDate"):
        user_data["birthDate"] = datetime.combine(user_data["birthDate"], datetime.min.time())
    
    result = await db[COLLECTION_NAME].insert_one(user_data)
    created_user = await db[COLLECTION_NAME].find_one({"_id": result.inserted_id})
    return created_user

async def update_user(db: AsyncIOMotorDatabase, user_id: str, user_in: UserUpdate):
    """
    Atualiza os dados de um usuário existente no banco de dados.
    """
    update_data = user_in.model_dump(exclude_unset=True)

    if not update_data:
        return await db[COLLECTION_NAME].find_one({"_id": ObjectId(user_id)})
    
    if "birthDate" in update_data and update_data["birthDate"]:
        update_data["birthDate"] = datetime.combine(update_data["birthDate"], datetime.min.time())

    await db[COLLECTION_NAME].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    
    return await db[COLLECTION_NAME].find_one({"_id": ObjectId(user_id)})