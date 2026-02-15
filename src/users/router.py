from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.users.schemas import (
    RegisterResponse,
    RegisterRequest,
    LoginRequest,
    LoginResponse,
    PaginatedListCreate,
    PaginatedListOut,
    UserOut,
    UserDetails,
    PasswordChange,
)
from src.users.service import (
    get_limitted_users_list,
    ban_user,
    user_details,
    my_account_detail,
    change_password,
    upgrade_user,
    downgrade_user,
)
from src.dependencies import get_db
from src.auth.authenticate import get_user, authenticate_user
from src.auth.hasher import get_password_hash
from src.auth.token import create_access_token
from src.users.models import User
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from src.constants import allow_any, user_required, admin_required, superadmin_required

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
def login(
    request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    if not db.query(User).filter(User.email == request.username).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with that e-mail doesn't exist",
        )

    if not authenticate_user(db, request.username, request.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Wrong e-mail or password"
        )

    user = db.query(User).filter(User.email == request.username).first()

    token_data = {"sub": str(user.id), "role": user.role.value}

    access_token = create_access_token(token_data, expires_delta=timedelta(minutes=60))

    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/paginated-list", response_model=PaginatedListOut, status_code=status.HTTP_200_OK
)
def get_list(
    request: PaginatedListCreate,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required),
):
    users_list = get_limitted_users_list(db=db, **request.model_dump())
    if not users_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return users_list


@router.put("/ban/{email}", response_model=UserOut, status_code=status.HTTP_200_OK)
def ban_user(
    email: str, db: Session = Depends(get_db), current_user=Depends(admin_required)
):
    user = ban_user(db, email, current_user)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return user


@router.get(
    "/details/{email}", response_model=UserDetails, status_code=status.HTTP_200_OK
)
def get_details(
    email: str, db: Session = Depends(get_db), current_user=Depends(admin_required)
):
    user = user_details(db, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return user


@router.get("/my-details", response_model=UserDetails, status_code=status.HTTP_200_OK)
def get_my_details(db: Session = Depends(get_db), current_user=Depends(user_required)):
    user = my_account_detail(db, current_user.id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return user


@router.put("/change-password", response_model=UserOut, status_code=status.HTTP_200_OK)
def password_change(
    request: PasswordChange,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required),
):
    user = change_password(db=db, user_id=current_user.id, **request.model_dump())
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return user


@router.put("/upgrade/{email}", response_model=UserOut, status_code=status.HTTP_200_OK)
def user_upgrade(
    email: str,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required),
):
    user = upgrade_user(db, email, current_user)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return user


@router.put(
    "/downgrade/{email}", response_model=UserOut, status_code=status.HTTP_200_OK
)
def user_downgrade(
    email: str,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required),
):
    user = downgrade_user(db, email, current_user)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return user
