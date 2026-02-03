from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float, Enum as sqlEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.enums import order_status

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(
        sqlEnum(order_status, name="order_status"),
        default=order_status.PENDING,
        nullable=False
        )
    total = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")