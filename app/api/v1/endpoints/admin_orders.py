# app/api/v1/endpoints/admin_orders.py
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from bson import ObjectId # <--- ADICIONE ESTA LINHA DE IMPORTAÇÃO

from app.db.session import get_database
from app.schemas import order as order_schema
from app.crud import crud_order
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[order_schema.Order])
async def list_all_orders(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin: dict = Depends(deps.get_current_admin_user)
):
    """
    Lista todos os pedidos do sistema. Requer permissão de administrador.
    """
    orders = await crud_order.get_all_orders(db, skip=skip, limit=limit, status=status)
    for order in orders:
        order["_id"] = str(order["_id"])
    return orders

@router.patch("/{order_id}/status", response_model=order_schema.Order)
async def update_order_status_by_admin(
    order_id: str,
    status_in: order_schema.OrderStatusUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin: dict = Depends(deps.get_current_admin_user)
):
    """
    Atualiza o status de um pedido. Requer permissão de administrador.
    """
    # Esta linha agora funcionará, pois o ObjectId foi importado
    order = await db["orders"].find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido com ID {order_id} não encontrado."
        )
    
    updated_order = await crud_order.update_order_status(db, order_id=order_id, status_update=status_in)
    
    # Nossa conversão para a resposta continua aqui
    if updated_order:
        updated_order["_id"] = str(updated_order["_id"])
        
    return updated_order