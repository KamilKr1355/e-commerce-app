from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    text,
    Enum,
)
from src.users.constants import Role
from sqlalchemy.orm import relationship
from src.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(Role), nullable=False, default=Role.user)
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))
    updated_at = Column(
        DateTime, nullable=False, server_default=text("now()"), onupdate=text("now()")
    )

    cart = relationship("Cart", back_populates="user", uselist=False)
    addresses = relationship(
        "Addresses", back_populates="user", cascade="all, delete-orphan"
    )
    orders = relationship("Order", back_populates="user")


class Addresses(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    full_name = Column(String, nullable=False)
    street = Column(String, nullable=False)
    city = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    country = Column(String, nullable=False)
    phone = Column(String, nullable=False)

    user = relationship("User", back_populates="addresses")
    
class RegistrationCode(Base):
    __tablename__ = "registration_code"
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    code = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=text("now()"))
