from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from app.models.enums import order_status_type
# Importamos los schemas del archivo anterior
from app.schemas.order_item import OrderItemCreate, OrderItemOut

class OrderBase(BaseModel):
    status: order_status_type = order_status_type.PENDING

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class OrderOut(OrderBase):
    id: UUID
    client_id: UUID
    total: Decimal
    created_at: datetime
    order_items: List[OrderItemOut]

class OrderUpdate(BaseModel):
    status: Optional[order_status_type] = None

    class Config:
        from_attributes = True