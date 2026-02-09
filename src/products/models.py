from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Boolean, DateTime, text
from sqlalchemy.orm import relationship
from src.database import Base

class Category(Base):
  __tablename__ = "categories"

  id = Column(Integer, primary_key=True)
  name = Column(String, nullable=False)
  slug = Column(String, unique=True, nullable=False)

  parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
  
  parent = relationship("Category", remote_side=[id], backref="children")
  
class Product(Base):
  __tablename__ = "products"
  
  id = Column(Integer, primary_key=True)
  name = Column(String, nullable=False)
  description = Column(String)
  price = Column(Numeric(10,2), nullable=False)
  currency = Column(String(5), nullable=False, default="PLN")
  stock = Column(Integer, nullable=False, default=0)
  is_active = Column(Boolean, nullable=False, default=True)
  created_at = Column(DateTime, nullable=False, server_default=text("now()"))
  updated_at = Column(DateTime, nullable=False, server_default=text("now()"), onupdate=text("now()"))
  
  category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
  