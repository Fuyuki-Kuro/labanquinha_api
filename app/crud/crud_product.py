# app/crud/crud_product.py
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Optional

from app.schemas.product import ProductCreate, ProductUpdate

COLLECTION_NAME = "products"

async def create_product(db: AsyncIOMotorDatabase, product: ProductCreate) -> dict:
    """Cria um novo produto no banco."""
    product_data = product.model_dump()
    product_data["status"] = "active" # Status padrão
    product_data["images"] = []      # Lista de imagens padrão
    
    result = await db[COLLECTION_NAME].insert_one(product_data)
    created_product = await db[COLLECTION_NAME].find_one({"_id": result.inserted_id})
    return created_product

async def get_product(db: AsyncIOMotorDatabase, product_id: str) -> Optional[dict]:
    """Busca um único produto pelo seu ID."""
    if not ObjectId.is_valid(product_id):
        return None
    return await db[COLLECTION_NAME].find_one({"_id": ObjectId(product_id)})

async def get_products(db: AsyncIOMotorDatabase, skip: int = 0, limit: int = 100) -> List[dict]:
    """Busca uma lista de produtos com paginação."""
    products_cursor = db[COLLECTION_NAME].find().skip(skip).limit(limit)
    return await products_cursor.to_list(length=limit)

async def update_product(db: AsyncIOMotorDatabase, product_id: str, product_update: ProductUpdate) -> Optional[dict]:
    """Atualiza um produto no banco."""
    if not ObjectId.is_valid(product_id):
        return None
        
    update_data = product_update.model_dump(exclude_unset=True)
    if not update_data:
        return await get_product(db, product_id) # Se não há dados para atualizar, retorna o produto atual

    await db[COLLECTION_NAME].update_one(
        {"_id": ObjectId(product_id)},
        {"$set": update_data}
    )
    return await db[COLLECTION_NAME].find_one({"_id": ObjectId(product_id)})

async def delete_product(db: AsyncIOMotorDatabase, product_id: str) -> bool:
    """Deleta um produto do banco."""
    if not ObjectId.is_valid(product_id):
        return False
        
    result = await db[COLLECTION_NAME].delete_one({"_id": ObjectId(product_id)})
    return result.deleted_count > 0