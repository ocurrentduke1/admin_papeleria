from fastapi import APIRouter, Depends, HTTPException
from app.crud.user import get_user_by_email
from app.schemas.auth import LoginRequest, TokenResponse
from sqlalchemy.orm import Session
from app.core.database import get_settings
from app.core.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_settings)):

    user = get_user_by_email(db, data.email)

    if not user:
        raise HTTPException(status_code=400, detail="Email o contraseña incorrectos")
    
    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="Email o contraseña incorrectos")
    
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )

    return TokenResponse(access_token=access_token)