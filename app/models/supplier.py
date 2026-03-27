import uuid
from sqlalchemy import Boolean, Column, String, DateTime, Uuid
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, index=True, nullable=False)
    contact_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    products = relationship("Product", back_populates="supplier")
