# app/schemas/user.py
from pydantic import BaseModel, Field, field_serializer
from datetime import date
from typing import Optional, List
from bson import ObjectId

# ... (O schema Address continua o mesmo) ...
class Address(BaseModel):
    street: str
    number: str
    complement: Optional[str] = None
    city: str
    state: str = Field(..., min_length=2, max_length=2)
    zipCode: str


# Propriedades base do usuário
class UserBase(BaseModel):
    name: str
    lastName: str
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$")
    birthDate: date
    # --- ADICIONE O CAMPO ROLE AQUI ---
    # Damos um valor padrão de "user" para todo novo usuário.
    role: str = "user"


# ... (O schema UserCreate continua o mesmo, ele herdará 'role' de UserBase) ...
class UserCreate(UserBase):
    cpf: str
    password: str


# Adicionamos 'role' ao schema de atualização para que um admin possa promovê-lo
class UserUpdate(BaseModel):
    name: Optional[str] = None
    lastName: Optional[str] = None
    birthDate: Optional[date] = None
    addresses: Optional[List[Address]] = None
    role: Optional[str] = None # <-- ADICIONE AQUI


# Adicionamos 'role' à resposta da API
class User(UserBase):
    id: str = Field(alias="_id")
    cpf: str
    addresses: List[Address] = []
    # 'role' já é herdado de UserBase

    @field_serializer('id')
    def serialize_id(self, id_obj: ObjectId) -> str:
        return str(id_obj)

    class Config:
        populate_by_name = True
        json_encoders = {
            date: lambda v: v.strftime('%Y-%m-%d')
        }
        arbitrary_types_allowed = True