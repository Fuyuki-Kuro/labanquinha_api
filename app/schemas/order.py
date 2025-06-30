# app/schemas/order.py
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from bson import ObjectId

from app.schemas import user as user_schema

class OrderItemCreate(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)

class OrderItem(OrderItemCreate):
    name: str
    price: float

class OrderBase(BaseModel):
    delivery_address: user_schema.Address

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class Order(OrderBase):
    id: str = Field(alias="_id")
    user_id: str
    order_number: int
    items: List[OrderItem]
    status: str
    subtotal: float
    delivery_fee: float
    total: float
    created_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class OrderStatusUpdate(BaseModel):
    status: str