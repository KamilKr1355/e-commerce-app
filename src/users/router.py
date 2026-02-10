from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.users.schemas import (
    RegisterResponse,
    RegisterRequest,
    LoginRequest,
    LoginResponse,
)
from src.dependencies import get_db
from src.auth.authenticate import get_user, authenticate_user
from src.auth.hasher import get_password_hash
from src.auth.token import create_access_token
from src.users.models import User
from datetime import timedelta

router = APIRouter(prefix="/user", tags=["users"])


@router.post("/register", response_model=RegisterResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    if get_user(db, request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with that e-mail already exists",
        )
    user = User(
        email=request.email, hashed_password=get_password_hash(request.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token_data = {"sub": str(user.id), "role": user.role.value}

    access_token = create_access_token(token_data, expires_delta=timedelta(minutes=60))

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    if not db.query(User).filter(User.email == request.email).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with that e-mail doesn't exist",
        )

    if not authenticate_user(db, request.email, request.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Wrong e-mail or password"
        )

    user = db.query(User).filter(User.email == request.email).first()

    token_data = {"sub": str(user.id), "role": user.role.value}

    access_token = create_access_token(token_data, expires_delta=timedelta(minutes=60))

    return {"access_token": access_token, "token_type": "bearer"}
