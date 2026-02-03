from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal

# 1. Esquema Base: Campos que comparten todos (lectura y escritura)
class ProductBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    sku: str = Field(..., min_length=3)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)
    supplier_id: UUID
    is_active: bool = True

# 2. Esquema para CREAR: Lo que pides en el POST
class ProductCreate(ProductBase):
    pass 

# 3. Esquema para ACTUALIZAR: Todo es opcional (PATCH)
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    is_active: Optional[bool] = None

# 4. Esquema para RESPONDER: Lo que sale de la API hacia el Frontend
class ProductOut(ProductBase):
    id: UUID
    created_at: datetime

    class Config:
        # Esto es VITAL: permite que Pydantic lea modelos de SQLAlchemy
        from_attributes = True