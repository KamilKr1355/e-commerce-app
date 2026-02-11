from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Numeric,
    Boolean,
    DateTime,
    text,
)
from sqlalchemy.orm import relationship
from src.database import Base


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)

    parent_id = Column(Integer, ForeignKey("category.id"), nullable=True)

    parent = relationship("Category", remote_side=[id], backref="children")

    products = relationship("Product", back_populates="category", cascade="all, delete")


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(5), nullable=False, default="PLN")
    stock = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))
    updated_at = Column(
        DateTime, nullable=False, server_default=text("now()"), onupdate=text("now()")
    )

    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)

    category = relationship("Category", back_populates="products")

    images = relationship(
        "ProductImage", back_populates="product", cascade="all, delete"
    )


class ProductImage(Base):
    __tablename__ = "product_image"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    url = Column(String, nullable=False, unique=True)
    is_main = Column(Boolean, default=False, nullable=False)

    product = relationship("Product", back_populates="images")
