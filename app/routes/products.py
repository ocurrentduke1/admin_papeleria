from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.deps import get_db, get_current_user
from app.crud.product import get_product, get_products, create_product, update_product, delete_product
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate
from app.models.user import User
from app.models.enums import users_role

router = APIRouter(prefix="/products", tags=["products"])

# Obtener todos los productos
@router.get("/", response_model=list[ProductOut])
def list_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_products(db)


# Obtener producto por ID
@router.get("/{product_id}", response_model=ProductOut)
def get_product_by_id(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


# Crear producto (solo admin y empleado)
@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_new_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [users_role.ADMIN, users_role.EMPLOYEE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="don´t have permissions to create product"
        )
    try:
        return create_product(db, product_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Actualizar producto (solo admin y empleado)
@router.patch("/{product_id}", response_model=ProductOut)
def update_existing_product(
    product_id: UUID,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [users_role.ADMIN, users_role.EMPLOYEE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="don´t have permissions to update product"
        )
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return update_product(db, product, product_data)


# Eliminar producto (solo admin)
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != users_role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="don´t have permissions to delete product"
        )
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    delete_product(db, product)