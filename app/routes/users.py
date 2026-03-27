from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_current_user, get_db
from app.crud.user import get_users, get_user, create_user, update_user, deactivate_user, change_password
from app.schemas.user import UserCreate, UserOut, UserUpdate, UserSelfUpdate, PasswordChange
from app.models.user import User
from app.models.enums import users_role

router = APIRouter(prefix="/users", tags=["users"])


# ── Perfil propio (debe ir ANTES de /{user_id}) ──────────────────────────────

@router.get("/me", response_model=UserOut)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
def update_my_profile(
    data: UserSelfUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return update_user(db, current_user, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
def update_my_password(
    data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        change_password(db, current_user, data.current_password, data.new_password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ── Gestión de usuarios (solo admin) ─────────────────────────────────────────

@router.get("/", response_model=list[UserOut])
def list_users(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != users_role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="don´t have permission to perform this action")
    return get_users(db, skip=skip, limit=limit)


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
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{user_id}", response_model=UserOut)
def update_existing_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != users_role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="don´t have permission to perform this action")
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return update_user(db, user, user_data)


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
