from sqlalchemy.orm import Session
from uuid import UUID
from app.models.user import User
from app.models.enums import users_role
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password, verify_password


# Crear usuario
def create_user(db: Session, user: UserCreate):

    # Verificar si ya existe el email
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise ValueError("The email is currently registered")

    # Hashear contraseña
    hashed_pwd = hash_password(user.password)

    db_user = User(
        name=user.name,
        email=user.email,
        password_hash=hashed_pwd,
        role=users_role.CLIENT,
        is_active=True
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Obtener usuario por ID
def get_user(db: Session, user_id: UUID):
    return (
        db.query(User)
        .filter(User.id == user_id, User.is_active == True)
        .first()
    )


# Obtener usuario por email (clave para login)
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email, User.is_active == True).first()


# Obtener todos los usuarios (solo activos)
def get_users(db: Session, skip: int = 0, limit: int = 20):
    return (
        db.query(User)
        .filter(User.is_active == True)
        .offset(skip)
        .limit(limit)
        .all()
    )

def update_user(db: Session, user: User, data: UserUpdate):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user

# Cambiar contraseña
def change_password(db: Session, user: User, current_password: str, new_password: str):
    if not verify_password(current_password, user.password_hash):
        raise ValueError("Current password is incorrect")
    user.password_hash = hash_password(new_password)
    db.commit()
    db.refresh(user)
    return user

# Desactivar usuario (soft delete)
def deactivate_user(db: Session, user: User):
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user