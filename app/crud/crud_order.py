# app/crud/crud_order.py
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from fastapi import HTTPException, status
from typing import List, Optional


from app.schemas.order import OrderCreate, OrderStatusUpdate
from app.crud import crud_product

COLLECTION_NAME = "orders"

async def get_next_order_number(db: AsyncIOMotorDatabase) -> int:
    """Obtém o próximo número de pedido sequencial."""
    last_order = await db[COLLECTION_NAME].find_one(sort=[("order_number", -1)])
    if last_order and "order_number" in last_order:
        return last_order["order_number"] + 1
    return 1

async def create_order(db: AsyncIOMotorDatabase, user_id: str, order_in: OrderCreate):
    """Cria um novo pedido, validando estoque e calculando totais."""
    processed_items = []
    subtotal = 0.0

    # 1. Validar cada item do pedido
    for item in order_in.items:
        product = await crud_product.get_product(db, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Produto com ID {item.product_id} não encontrado.")
        if product["stock"] < item.quantity:
            raise HTTPException(status_code=400, detail=f"Estoque insuficiente para o produto '{product['name']}'.")
        
        # Adiciona o item processado com os dados do momento da compra
        processed_items.append({
            "product_id": item.product_id,
            "quantity": item.quantity,
            "name": product["name"],
            "price": product["price"]
        })
        subtotal += product["price"] * item.quantity

    # 2. Calcular totais
    delivery_fee = 9.99 # Valor fixo por enquanto
    total = subtotal + delivery_fee

    # 3. Criar o documento do pedido
    order_number = await get_next_order_number(db)
    order_document = {
        "user_id": user_id,
        "order_number": order_number,
        "items": processed_items,
        "delivery_address": order_in.delivery_address.model_dump(),
        "status": "pending", # Status inicial
        "subtotal": subtotal,
        "delivery_fee": delivery_fee,
        "total": total,
        "created_at": datetime.utcnow()
    }
    
    # 4. Inserir o pedido no banco
    result = await db[COLLECTION_NAME].insert_one(order_document)

    # 5. Atualizar o estoque dos produtos (operação crítica)
    for item in processed_items:
        await db["products"].update_one(
            {"_id": ObjectId(item["product_id"])},
            {"$inc": {"stock": -item["quantity"]}}
        )

    return await db[COLLECTION_NAME].find_one({"_id": result.inserted_id})

async def get_order(db: AsyncIOMotorDatabase, order_id: str, user_id: str):
    """Busca um pedido específico, garantindo que pertence ao usuário."""
    if not ObjectId.is_valid(order_id):
        return None
    return await db[COLLECTION_NAME].find_one({"_id": ObjectId(order_id), "user_id": user_id})

async def get_orders_by_user(db: AsyncIOMotorDatabase, user_id: str):
    """Lista todos os pedidos de um usuário."""
    orders_cursor = db[COLLECTION_NAME].find({"user_id": user_id}).sort("created_at", -1)
    return await orders_cursor.to_list(length=100) # Limite de 100 por enquanto

async def get_all_orders(
    db: AsyncIOMotorDatabase,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None
) -> List[dict]:
    """
    Busca todos os pedidos no banco de dados (para admin), com opção de filtro por status.
    """
    query = {}
    if status:
        query["status"] = status
        
    orders_cursor = db[COLLECTION_NAME].find(query).sort("created_at", -1).skip(skip).limit(limit)
    return await orders_cursor.to_list(length=limit)


async def update_order_status(db: AsyncIOMotorDatabase, order_id: str, status_update: OrderStatusUpdate) -> Optional[dict]:
    """
    Atualiza o status de um pedido específico (para admin).
    """
    if not ObjectId.is_valid(order_id):
        return None

    await db[COLLECTION_NAME].update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": status_update.status, "updated_at": datetime.utcnow()}}
    )
    
    return await db[COLLECTION_NAME].find_one({"_id": ObjectId(order_id)})