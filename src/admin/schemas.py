from pydantic import BaseModel
from typing import List
from decimal import Decimal

class RevenuePoint(BaseModel):
    date: str
    amount: float

class ProductProfitStat(BaseModel):
    name: str
    profit: float

class ProductConversionStat(BaseModel):
    name: str
    views: int
    sold_quantity: int
    conversion_rate: float

class DashboardStats(BaseModel):
    total_revenue: float
    average_order_value: float
    revenue_chart: List[RevenuePoint]
    top_profitable_products: List[ProductProfitStat]
    product_conversions: List[ProductConversionStat]