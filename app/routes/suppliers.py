from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.deps import get_db, get_current_user
from app.crud.supplier import get_supplier, get_suppliers, create_supplier, update_supplier, deactivate_supplier
from app.schemas.supplier import SupplierCreate, SupplierOut, SupplierUpdate
from app.models.user import User
from app.models.enums import users_role

router = APIRouter(prefix="/suppliers", tags=["suppliers"])

# Obtener todos los proveedores
@router.get("/", response_model=list[SupplierOut])
def list_suppliers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_suppliers(db)


# Obtener proveedor por ID
@router.get("/{supplier_id}", response_model=SupplierOut)
def get_supplier_by_id(
    supplier_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    supplier = get_supplier(db, supplier_id)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proveedor no encontrado"
        )
    return supplier


# Crear proveedor (solo admin)
@router.post("/", response_model=SupplierOut, status_code=status.HTTP_201_CREATED)
def create_new_supplier(
    supplier_data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != users_role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción"
        )
    return create_supplier(db, supplier_data)


# Actualizar proveedor (solo admin)
@router.patch("/{supplier_id}", response_model=SupplierOut)
def update_existing_supplier(
    supplier_id: UUID,
    supplier_data: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != users_role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción"
        )
    supplier = get_supplier(db, supplier_id)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proveedor no encontrado"
        )
    return update_supplier(db, supplier, supplier_data)


# Desactivar proveedor (solo admin)
@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_existing_supplier(
    supplier_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != users_role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción"
        )
    supplier = get_supplier(db, supplier_id)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proveedor no encontrado"
        )
    deactivate_supplier(db, supplier)