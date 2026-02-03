from sqlalchemy import Column, DateTime, Integer, String, Boolean, Enum as SqlEnum
from app.core.database import Base
from app.models.enums import users_role

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(
        SqlEnum(users_role, name="role"),
        default=users_role.CLIENT,
        nullable=False
    )
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False)