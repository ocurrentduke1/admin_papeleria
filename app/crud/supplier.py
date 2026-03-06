from sqlalchemy.orm import Session
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate
from uuid import UUID

# crear proveedor
def create_supplier(db: Session, supplier: SupplierCreate):
    db_supplier = Supplier(**supplier.model_dump())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

# obtener proveedor por id
def get_supplier(db: Session, supplier_id: UUID):
    return db.query(Supplier).filter(Supplier.id == supplier_id).first()

# obtener todos los proveedores
def get_suppliers(db: Session):
    return db.query(Supplier).all()

# actualizar proveedor
def update_supplier(db: Session, supplier: Supplier, data: SupplierUpdate):
    for field, value, in data.model_dump(exclude_unset=True).items():
        setattr(supplier, field, value)
    db.commit()
    db.refresh(supplier)
    return supplier

# desactivar proveedor
def deactivate_supplier(db: Session, supplier: Supplier):
    supplier.is_active = False
    db.commit()
    db.refresh(supplier)
    return supplier