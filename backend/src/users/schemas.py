from pydantic import BaseModel, EmailStr
from typing import List, Optional
from src.users.constants import Role
from datetime import datetime
from src.shopping.schemas import OrderOut

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: str | None = None


class User(BaseModel):
    email: str | None = None
    is_active: bool | None = None

class UserOut(User):
    id: int
    role: Role
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserDetails(BaseModel):
    id: int
    email: EmailStr
    role: Role
    created_at: datetime
    orders: List[OrderOut]

class UserInDB(User):
    hashed_password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterResponse(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str

class PasswordChange(BaseModel):
    current_password : str
    new_password: str
    
class PaginatedListOut(BaseModel):
    items: List[UserOut]
    total: int
    offset: int
    limit: int
    total_pages: int
    
    class Config:
        from_attributes = True

class PaginatedListCreate(BaseModel):
    offset: Optional[int]
    limit: Optional[int]
    

    

