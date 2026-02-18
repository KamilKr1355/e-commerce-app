from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional
from decimal import Decimal
from typing import List
from src.products.schemas import ProductOut
from src.logistics.schemas import ShipmentCreate
from src.shopping.constants import OrderStatus
from enum import Enum


class CartBase(BaseModel):
    user_id: int


class CartCreate(CartBase):
    class Config:
        from_attributes = True


class CartItemBase(BaseModel):
    cart_id: int
    product_id: int
    quantity: int = Field(gt=0, default=1)


class CartItemCreate(CartItemBase):
    class Config:
        from_attributes = True


class CartItemOut(CartItemBase):
    id: int
    price_at_time: Decimal
    product: ProductOut


class CartOut(CartBase):
    id: int
    items: List[CartItemOut]


class Price(BaseModel):
    total_price: Decimal


class OrderBase(BaseModel):
    user_id: Optional[int] = None


class OrderCreate(BaseModel):
    user_id: int


class OrderItemOut(BaseModel):
    id: int
    order_id: int
    product_id: int
    product_name_snapshot: str
    price: Decimal
    quantity: int
    product: ProductOut


class OrderOut(OrderBase):
    id: int
    status: Enum
    total_amount: Decimal
    currency: str = Field(min_length=2, max_length=5)
    created_at: datetime
    items: List[OrderItemOut]


class Status(BaseModel):
    status: str


class IncrementDecrement(BaseModel):
    product_id: int


class OrderStatus(BaseModel):
    status: OrderStatus


class GuestOrderItem(BaseModel):
    product_id: int
    quantity: int


class GuestOrder(BaseModel):
    email: EmailStr
    items: List[GuestOrderItem]
    shipping_data: ShipmentCreate
