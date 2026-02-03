from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional

class SupplierBase(BaseModel):
    name: str
    contact_name: str
    email: EmailStr
    phone: Optional[str] = None
    is_active: bool = True

class SupplierCreate(SupplierBase):
    pass

class SupplierOut(SupplierBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True