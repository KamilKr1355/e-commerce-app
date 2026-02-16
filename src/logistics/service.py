from fastapi import Depends, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from src.logistics.schemas import PaymentCreate, ShipmentCreate, WebhookCreate
from src.shopping.models import Order, OrderItem
from src.logistics.models import Payment, Shipment, WebhookEvent
from src.email.service import send_payment_success_email
from src.logistics.constants import (
    Providers,
    PaymentMethod,
    Status,
    Courier,
    CourierPrice,
)
from src.shopping.constants import OrderStatus
from datetime import datetime
from src.logistics.stripe import create_checkout_session
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.ERROR)

logger = logging.getLogger(__name__)

load_dotenv()


def initiate_payment(db: Session, payment_data: PaymentCreate, user_id: int):
    order = (
        db.query(Order)
        .filter(Order.id == payment_data.order_id, Order.user_id == user_id)
        .first()
    )
    if not order:
        return None, None

    url, stripe_session_id = create_checkout_session(db, order)
    if isinstance(url, dict):
        return None, None

    payment_dict = payment_data.model_dump()
    payment_dict["provider_payment_id"] = stripe_session_id

    db_payment = Payment(
        order_id=order.id,
        amount=order.total_amount,
        currency=order.currency,
        provider_payment_id=stripe_session_id,
        status=Status.pending,
        provider=Providers.stripe,
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    return db_payment, url


def payment_succeed(db: Session, provider_payment_id: str):
    db_payment = (
        db.query(Payment)
        .filter(Payment.provider_payment_id == provider_payment_id)
        .first()
    )
    assigned_order = db.query(Order).filter(Order.id == db_payment.order_id).first()

    if not (db_payment and assigned_order):
        return None

    db_payment.status = Status.success
    assigned_order.status = OrderStatus.paid

    db.commit()
    db.refresh(db_payment)
    return db_payment


def payment_failed(db: Session, provider_payment_id: str):
    db_payment = (
        db.query(Payment)
        .filter(Payment.provider_payment_id == provider_payment_id)
        .first()
    )
    assigned_order = db.query(Order).filter(Order.id == db_payment.order_id).first()

    if not (db_payment and assigned_order):
        return None

    db_payment.status = Status.failed
    assigned_order.status = OrderStatus.cancelled

    db.commit()
    db.refresh(db_payment)
    return db_payment


def get_paid_shipments(db: Session, date: datetime, limit: int):
    return (
        db.query(Shipment)
        .join(Order)
        .options(
            joinedload(Shipment.order)
            .joinedload(Order.items)
            .joinedload(OrderItem.product)
        )
        .filter(Order.status == OrderStatus.paid, Order.created_at > date)
        .order_by(Order.created_at.asc())
        .limit(limit)
        .all()
    )


def create_shipment(db: Session, shipment_data: ShipmentCreate):
    order = db.query(Order).filter(Order.id == shipment_data.order_id).first()

    if not order:
        return None

    db_shipment = Shipment(**shipment_data.model_dump())

    match db_shipment.courier:
        case Courier.inpost:
            db_shipment.order.total_amount += CourierPrice.inpost
        case Courier.inpost_paczkomat:
            db_shipment.order.total_amount += CourierPrice.inpost_paczkomat
        case Courier.dhl:
            db_shipment.order.total_amount += CourierPrice.dhl
        case Courier.dhl_paczkomat:
            db_shipment.order.total_amount += CourierPrice.dhl_paczkomat
        case Courier.dpd:
            db_shipment.order.total_amount += CourierPrice.dpd
        case Courier.orlen:
            db_shipment.order.total_amount += CourierPrice.orlen
        case _:
            pass

    db.add(db_shipment)
    db.commit()
    db.refresh(db_shipment)

    return db_shipment


def update_tracking(
    db: Session, shipment_id: int, tracking_number: str = None, status: Status = None
):
    db_shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if db_shipment:
        match status:
            case Status.success:
                db_shipment.status = Status.success
                db_shipment.shipped_at = datetime.now()
            case Status.failed:
                db_shipment.status = Status.failed
            case _:
                db_shipment.tracking_number = tracking_number
                db_shipment.status = Status.pending
    else:
        return None

    db.commit()
    db.refresh(db_shipment)
    return db_shipment


def get_shippment(db: Session, order_id: int):
    db_shipment = db.query(Shipment).filter(Shipment.order_id == order_id).first()
    if not db_shipment:
        return None

    return db_shipment


def mark_webhook_as_processed(db: Session, event_id: str):
    db_event = db.query(WebhookEvent).filter(WebhookEvent.event_id == event_id).first()
    if db_event:
        db_event.processed = True
        db.commit()


def handle_webhook_event(db: Session, webhook_data: WebhookCreate, background_tasks: BackgroundTasks):
    existing_event = (
        db.query(WebhookEvent)
        .filter(WebhookEvent.event_id == webhook_data.event_id)
        .first()
    )
    if existing_event:
        return existing_event

    db_event = WebhookEvent(**webhook_data.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    if db_event.event_type == "checkout.session.completed":
        order_id = payment_intent_id = db_event.payload["data"]["object"]["client_reference_id"]
        order = db.query(Order).filter(Order.id == order_id).first()
    
        try:
            email = order.shipment.shipping_email
            background_tasks.add_task(send_payment_success_email, order_id, email)
        except Exception as e:
            logging.error(f"error in payment: {e}")
      
        payment_intent_id = db_event.payload["data"]["object"]["id"]
        payment_succeed(db, payment_intent_id)
        mark_webhook_as_processed(db, db_event.event_id)
    return db_event
