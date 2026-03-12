from operator import gt

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.models.enums import movements_type

class InventoryMovementBase(BaseModel):
    product_id: UUID
    type: movements_type
    quantity: int = Field(..., gt=0)
    reason: Optional[str] = None
    reference_id: Optional[UUID] = None

class InventoryMovementCreate(InventoryMovementBase):
    # El created_by lo tomaremos del token del usuario autenticado en el endpoint
    pass

class InventoryMovementOut(InventoryMovementBase):
    id: UUID
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True