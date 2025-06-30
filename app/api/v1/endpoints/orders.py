# app/api/v1/endpoints/orders.py
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List

from app.db.session import get_database
from app.schemas import order as order_schema
from app.crud import crud_order
from app.api import deps

router = APIRouter()

@router.post("/", response_model=order_schema.Order, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: order_schema.OrderCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(deps.get_current_user)
):
    """Cria um novo pedido para o usuário logado."""
    user_id = str(current_user["_id"])
    new_order = await crud_order.create_order(db, user_id=user_id, order_in=order_in)
    
    # --- CORREÇÃO EXPLÍCITA ---
    if new_order:
        new_order["_id"] = str(new_order["_id"])
        
    return new_order

@router.get("/", response_model=List[order_schema.Order])
async def list_user_orders(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(deps.get_current_user)
):
    """Lista todos os pedidos do usuário logado."""
    user_id = str(current_user["_id"])
    orders = await crud_order.get_orders_by_user(db, user_id=user_id)
    
    # --- CORREÇÃO EXPLÍCITA PARA A LISTA ---
    for order in orders:
        order["_id"] = str(order["_id"])
        
    return orders

@router.get("/{order_id}", response_model=order_schema.Order)
async def get_user_order(
    order_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(deps.get_current_user)
):
    """Busca um pedido específico do usuário logado."""
    user_id = str(current_user["_id"])
    order = await crud_order.get_order(db, order_id=order_id, user_id=user_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado ou não pertence a este usuário."
        )
    
    # --- CORREÇÃO EXPLÍCITA ---
    order["_id"] = str(order["_id"])
    
    return order