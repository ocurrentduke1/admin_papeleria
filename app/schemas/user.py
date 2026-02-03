from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.models.enums import users_role

class UserBase(BaseModel):
    name: Optional[str] = Field(None, max_length=150)
    email: EmailStr
    role: users_role = users_role.CLIENT
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserOut(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True