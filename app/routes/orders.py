from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.deps import get_db, get_current_user
from app.crud.order import get_order, get_orders, create_order, update_order, cancel_order
from app.schemas.order import OrderCreate, OrderOut, OrderUpdate
from app.models.user import User
from app.models.enums import users_role

router = APIRouter(prefix="/orders", tags=["orders"])

# Obtener todas las ordenes (admin y empleado)
@router.get("/", response_model=list[OrderOut])
def list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [users_role.ADMIN, users_role.EMPLOYEE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="don´t have permissions to view orders"
        )
    return get_orders(db)


# Obtener orden por ID
@router.get("/{order_id}", response_model=OrderOut)
def get_order_by_id(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    # Cliente solo puede ver sus propias ordenes
    if current_user.role == users_role.CLIENT and order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="don´t have permissions to view this order"
        )
    return order


# Crear orden
@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_new_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return create_order(db, order_data, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Actualizar estado de orden (admin y empleado)
@router.patch("/{order_id}", response_model=OrderOut)
def update_order_status(
    order_id: UUID,
    order_data: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [users_role.ADMIN, users_role.EMPLOYEE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="don´t have permissions to update order status"
        )
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    try:
        return update_order(db, order_id, order_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Cancelar orden
@router.delete("/{order_id}", response_model=OrderOut)
def cancel_existing_order(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    # Solo admin o el mismo cliente pueden cancelar
    if current_user.role == users_role.CLIENT and order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="don´t have permissions to cancel this order"
        )
    try:
        return cancel_order(db, order_id, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )