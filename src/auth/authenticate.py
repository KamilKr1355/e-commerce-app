from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.users.models import User
from src.users.schemas import UserInDB
from src.auth.hasher import verify_password
from src.users.constants import Role
from src.auth.token import get_current_user


def get_user(db: Session, email: str = None):
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user
    return None


def authenticate_user(db: Session, email: str = None, password: str = None):
    user = get_user(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


class RoleChecker:
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if not self.allowed_roles:
            return user
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User doesn't have permissions",
            )

        return user
