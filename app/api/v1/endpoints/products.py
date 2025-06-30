# app/api/v1/endpoints/products.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.session import get_database
from app.schemas import product as product_schema
from app.crud import crud_product
from app.api import deps

router = APIRouter()

@router.post("/", response_model=product_schema.Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: product_schema.ProductCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    # Rota protegida: Somente administradores podem criar produtos
    current_user: dict = Depends(deps.get_current_admin_user)
):
    """Cria um novo produto. Requer autenticação de administrador."""
    new_product = await crud_product.create_product(db, product_in)
    
    if new_product:
        new_product["_id"] = str(new_product["_id"])
        
    return new_product

@router.get("/", response_model=List[product_schema.Product])
async def read_products(
    skip: int = 0,
    limit: int = 100,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Lista os produtos. Rota pública."""
    products = await crud_product.get_products(db, skip=skip, limit=limit)
    
    for product in products:
        product["_id"] = str(product["_id"])
        
    return products

@router.get("/{product_id}", response_model=product_schema.Product)
async def read_product(
    product_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Busca um produto por ID. Rota pública."""
    db_product = await crud_product.get_product(db, product_id)
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
    
    db_product["_id"] = str(db_product["_id"])
    
    return db_product

@router.put("/{product_id}", response_model=product_schema.Product)
async def update_product(
    product_id: str,
    product_in: product_schema.ProductUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    # Rota protegida: Somente administradores podem atualizar produtos
    current_user: dict = Depends(deps.get_current_admin_user)
):
    """Atualiza um produto. Requer autenticação de administrador."""
    db_product = await crud_product.get_product(db, product_id)
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
    
    updated_product = await crud_product.update_product(db, product_id, product_in)
    
    if updated_product:
        updated_product["_id"] = str(updated_product["_id"])
        
    return updated_product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    # Rota protegida: Somente administradores podem deletar produtos
    current_user: dict = Depends(deps.get_current_admin_user)
):
    """Deleta um produto. Requer autenticação de administrador."""
    deleted = await crud_product.delete_product(db, product_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
    return