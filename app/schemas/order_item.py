from pydantic import BaseModel, Field
from uuid import UUID
from decimal import Decimal

class OrderItemBase(BaseModel):
    product_id: UUID
    quantity: int = Field(..., gt=0)

class OrderItemCreate(OrderItemBase):
    # Solo necesitamos saber qué producto y cuánto
    pass

class OrderItemOut(OrderItemBase):
    id: UUID
    order_id: UUID
    unit_price: Decimal
    subtotal: Decimal

    class Config:
        from_attributes = True