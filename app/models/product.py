from sqlalchemy import Column, DateTime, Integer, String, Numeric, Boolean, ForeignKey, Uuid
from sqlalchemy.orm import relationship
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Uuid, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    sku = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Numeric, nullable=False)
    stock = Column(Integer, default=0, nullable=False)
    supplier_id = Column(Uuid, ForeignKey("suppliers.id"), ondelete="RESTRICT", nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False)

    supplier = relationship("Supplier", back_populates="products")