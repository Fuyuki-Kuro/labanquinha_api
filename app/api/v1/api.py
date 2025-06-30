# app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1.endpoints import auth, products, users, orders, admin_orders


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])

api_router.include_router(admin_orders.router, prefix="/admin/orders", tags=["Admin: Orders"])