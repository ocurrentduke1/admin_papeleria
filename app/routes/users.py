
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_current_user, get_db
from app.crud.user import get_users, get_user, create_user, update_user, deactivate_user
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.models.user import User, users_role

router = APIRouter(prefix="/users", tags=["users"])

# Obtener todos los usuarios (solo admin)
@router.get("/", response_model=list[UserOut])
def list_users(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != users_role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="don´t have permission to perform this action")
    
    return get_users(db, skip=skip, limit=limit)

# Obtener un usuario por ID (solo admin)
@router.get("/{user_id}", response_model=UserOut)
def get_user_by_id(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != users_role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="don´t have permission to perform this action")
    
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user

# Crear un nuevo usuario (solo admin)
@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_new_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != users_role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="don´t have permission to perform this action")
    try:
        return create_user(db, user_data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
# Actualizar un usuario (solo admin)
@router.patch("/{user_id}", response_model=UserOut)
def update_existing_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if (current_user.role != users_role.ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="don´t have permission to perform this action")
    
    user = get_user(db, user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return update_user(db, user, user_data)

# Desactivar un usuario (solo admin)
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != users_role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="don´t have permission to perform this action")
    
    user = get_user(db, user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    deactivate_user(db, user)

# ver perfil propio
@router.get("/me", response_model=UserOut)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user