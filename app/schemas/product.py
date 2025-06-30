# app/schemas/product.py
from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    category: str
    brand: Optional[str] = None

class ProductCreate(ProductBase):
    sku: str

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = None
    brand: Optional[str] = None
    status: Optional[str] = None

class Product(ProductBase):
    id: str = Field(alias="_id")
    sku: str
    status: str = "active"
    images: List[str] = []

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}