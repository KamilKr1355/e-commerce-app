from enum import Enum as pyEnum


class OrderStatus(pyEnum):
    pending = "pending"
    paid = "paid"
    shipped = "shipped"
    cancelled = "cancelled"
