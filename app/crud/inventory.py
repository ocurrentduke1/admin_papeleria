from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session

from app.models.inventory_movement import InventoryMovement
from app.models.product import Product
from app.models.enums import movements_type
from app.schemas.inventory_movement import InventoryAdjustmentCreate


def get_movements(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    product_id: Optional[UUID] = None,
    movement_type: Optional[movements_type] = None,
):
    query = db.query(InventoryMovement)

    if product_id:
        query = query.filter(InventoryMovement.product_id == product_id)
    if movement_type:
        query = query.filter(InventoryMovement.type == movement_type)

    return (
        query
        .order_by(InventoryMovement.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_movements_by_product(db: Session, product_id: UUID, skip: int = 0, limit: int = 50):
    return (
        db.query(InventoryMovement)
        .filter(InventoryMovement.product_id == product_id)
        .order_by(InventoryMovement.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_adjustment(db: Session, data: InventoryAdjustmentCreate, user_id: UUID):
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise ValueError(f"Product {data.product_id} does not exist")

    if data.type == movements_type.OUT:
        if product.stock < data.quantity:
            raise ValueError(
                f"Insufficient stock. Available: {product.stock}, requested: {data.quantity}"
            )
        product.stock -= data.quantity
        stored_quantity = -data.quantity
    else:
        # IN y ADJUSTMENT suman al stock
        product.stock += data.quantity
        stored_quantity = data.quantity

    movement = InventoryMovement(
        product_id=product.id,
        type=data.type,
        quantity=stored_quantity,
        reason=data.reason,
        created_by=user_id,
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement
