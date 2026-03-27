from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud.inventory import get_movements, get_movements_by_product, create_adjustment
from app.models.enums import users_role, movements_type
from app.models.user import User
from app.schemas.inventory_movement import InventoryMovementOut, InventoryAdjustmentCreate

router = APIRouter(prefix="/inventory", tags=["inventory"])

ALLOWED_ROLES = [users_role.ADMIN, users_role.EMPLOYEE]


# Listar movimientos (con filtros opcionales)
@router.get("/", response_model=list[InventoryMovementOut])
def list_movements(
    skip: int = 0,
    limit: int = 50,
    product_id: Optional[UUID] = None,
    type: Optional[movements_type] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="don´t have permissions to view inventory movements",
        )
    return get_movements(db, skip=skip, limit=limit, product_id=product_id, movement_type=type)


# Historial de movimientos de un producto específico
@router.get("/product/{product_id}", response_model=list[InventoryMovementOut])
def list_movements_by_product(
    product_id: UUID,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="don´t have permissions to view inventory movements",
        )
    return get_movements_by_product(db, product_id=product_id, skip=skip, limit=limit)


# Ajuste manual de inventario
@router.post("/adjustment", response_model=InventoryMovementOut, status_code=status.HTTP_201_CREATED)
def manual_adjustment(
    data: InventoryAdjustmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="don´t have permissions to adjust inventory",
        )
    try:
        return create_adjustment(db, data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
