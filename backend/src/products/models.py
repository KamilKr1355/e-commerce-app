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
from datetime import datetime, timedelta


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
    views = Column(Integer, nullable=True, default=0)
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

    discounts = relationship(
        "Discount", back_populates="product", cascade="all, delete"
    )

    @property
    def current_price(self):
        now = datetime.now()
        for discount in self.discounts:
            if discount.is_active:
                return discount.new_price
        return self.price

    @property
    def lowest_price_30days(self):
        thirty_days_ago = datetime.now() - timedelta(days=30)

        prices = [self.price]

        for discount in self.discounts:
            if discount.valid_from >= thirty_days_ago:
                prices.append(discount.new_price)

        return min(prices)


class Discount(Base):
    __tablename__ = "discount"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    new_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, nullable=False, default=text("now()"))
    valid_from = Column(DateTime, nullable=False, server_default=text("now()"))
    valid_until = Column(DateTime, nullable=True)

    product = relationship("Product", uselist=False, back_populates="discount")

    @property
    def is_active(self):
        if datetime.now() < self.valid_until:
            return True
        return False


class ProductImage(Base):
    __tablename__ = "product_image"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    url = Column(String, nullable=False, unique=True)
    is_main = Column(Boolean, default=False, nullable=False)

    product = relationship("Product", back_populates="images")
