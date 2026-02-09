from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, text
from sqlalchemy.orm import relationship
from src.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))
    updated_at = Column(
        DateTime, nullable=False, server_default=text("now()"), onupdate=text("now()")
    )

    role = relationship("Role", back_populates="users")
    
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