from pydantic import BaseModel
from decimal import Decimal
from typing import Optional, Dict, Any
from src.logistics.constants import Providers, PaymentMethod, Status, Courier, DeliveryType

class PaymentBase(BaseModel):
    order_id: int
    provider: Providers
    amount: Decimal
    currency: str = "PLN"

class PaymentCreate(BaseModel):
    order_id: int
    

class PaymentOut(PaymentBase):
    order_id: int
    provider: Providers
    amount: Decimal
    currency: str = "PLN"
    provider_payment_id: str
    id: int
    status: Status
    class Config:
        from_attributes = True

class FinalizedPayment(BaseModel):
  payment: PaymentOut
  url: str
  
  class Config:
        from_attributes = True

class ShipmentCreate(BaseModel):
    order_id: int
    courier: Courier
    delivery_type: DeliveryType
    shipping_full_name: str
    shipping_street: str
    shipping_city: str
    shipping_postal_code: str
    shipping_country: str
    shipping_phone: str
    pickup_point_code: Optional[str] = None

class ShipmentOut(ShipmentCreate):
    id: int
    tracking_number: Optional[str]
    status: Status
    class Config:
        from_attributes = True

class WebhookCreate(BaseModel):
    provider: str
    event_id: str
    event_type: str
    payload: Dict[str, Any]