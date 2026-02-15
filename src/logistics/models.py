from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Enum,
    String,
    Numeric,
    DateTime,
    text,
    Boolean,
    JSON,
)
from src.database import Base
from src.logistics.constants import (
    Providers,
    PaymentMethod,
    Status,
    Courier,
    DeliveryType,
)
from sqlalchemy.orm import relationship


class Payment(Base):
    __tablename__ = "payment"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("order.id"))
    provider = Column(Enum(Providers), nullable=False, default=Providers.stripe)
    payment_method = Column(Enum(PaymentMethod), nullable=True)
    status = Column(Enum(Status), nullable=False, default=Status.pending)
    provider_payment_id = Column(String, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False, default=0)
    currency = Column(String(5), nullable=False, default="PLN")
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))

    order = relationship("Order", back_populates="payment")


class Shipment(Base):
    __tablename__ = "shipment"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("order.id"), nullable=False, unique=True)
    courier = Column(Enum(Courier), nullable=False)
    delivery_type = Column(Enum(DeliveryType), nullable=False)

    pickup_point_code = Column(String, nullable=True)
    pickup_point_name = Column(String, nullable=True)
    pickup_point_address = Column(String, nullable=True)

    tracking_number = Column(String, nullable=True)

    shipping_full_name = Column(String, nullable=False)
    shipping_email = Column(String, nullable=False)
    shipping_street = Column(String, nullable=False)
    shipping_city = Column(String, nullable=False)
    shipping_postal_code = Column(String, nullable=False)
    shipping_country = Column(String, nullable=False)
    shipping_phone = Column(String, nullable=False)
    shipping_company = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    nip = Column(String, nullable=True)

    status = Column(Enum(Status), nullable=False, default=Status.pending)
    shipped_at = Column(DateTime)
    delivered_at = Column(DateTime)

    order = relationship("Order", back_populates="shipment", uselist=False)


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True)
    provider = Column(Enum(Providers), nullable=False, default=Providers.stripe)
    event_id = Column(String, unique=True, nullable=False)
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    processed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))
