from sqlalchemy import Column,Uuid, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Uuid, primary_key=True, index=True)
    order_id = Column(Uuid, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Uuid, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="order_items")
    product = relationship("Product")