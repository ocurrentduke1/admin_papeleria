from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from app.models.enums import order_status
# Importamos los schemas del archivo anterior
from app.schemas.order_item import OrderItemCreate, OrderItemOut

class OrderBase(BaseModel):
    status: order_status = order_status.PENDING

class OrderCreate(BaseModel):
    # El cliente envía una lista de estos
    items: List[OrderItemCreate]

class OrderOut(OrderBase):
    id: UUID
    client_id: UUID
    total: Decimal
    created_at: datetime
    # Aquí usamos el esquema de salida del otro archivo
    order_items: List[OrderItemOut] 

    class Config:
        from_attributes = True