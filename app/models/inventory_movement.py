from sqlalchemy import Column,Uuid, Integer, ForeignKey, DateTime, String, Enum as sqlEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.enums import movements_type

class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id = Column(Uuid, primary_key=True, index=True)
    product_id = Column(Uuid, ForeignKey("products.id"), nullable=False)
    type = Column(sqlEnum(movements_type, name="movements_type"), nullable=False)
    quantity = Column(Integer, nullable=False)
    reason = Column(String, nullable=True)
    reference_id = Column(Uuid, nullable=True)
    created_by = Column(Uuid, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False)

    product = relationship("Product", back_populates="inventory_movements")
    creator = relationship("User")