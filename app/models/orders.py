from datetime import datetime
from sqlalchemy import Column,Uuid, ForeignKey, DateTime, Numeric, Enum as sqlEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.enums import order_status_type

class Order(Base):
    __tablename__ = "orders"

    id = Column(Uuid, primary_key=True, index=True)
    user_id = Column(Uuid, ForeignKey("users.id"), nullable=False)
    status = Column(
        sqlEnum(order_status_type, name="order_status_type"),
        default=order_status_type.PENDING,
        nullable=False
        )
    total = Column(Numeric, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")