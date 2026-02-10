from fastapi import Depends
from sqlalchemy.orm import Session
from src.users.models import User
from src.users.schemas import UserInDB
from src.auth.hasher import verify_password


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
