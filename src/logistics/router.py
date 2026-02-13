from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from src.dependencies import get_db
from src.users.models import User
from src.logistics.models import Shipment
from src.constants import admin_required, allow_any, user_required
from src.logistics.schemas import (
    PaymentOut, PaymentCreate, 
    ShipmentOut, ShipmentCreate, FinalizedPayment
)
from src.logistics.schemas import WebhookCreate
from src.logistics.service import initiate_payment, create_shipment, get_shippment, handle_webhook_event, mark_webhook_as_processed, payment_succeed, payment_failed
import stripe
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/logistics", tags=["logistics"])
ENDPOINT_SECRET = os.getenv("sk_stripe")
@router.post("/payments", response_model=FinalizedPayment)
def create_payment(request: PaymentCreate, db: Session = Depends(get_db), current_user: User = Depends(user_required)):
    payment, url = initiate_payment(db, request, current_user.id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not initiate payment")
    return {"payment":payment, "url":url}

@router.post("/shipments", response_model=ShipmentOut)
def post_shipment(request: ShipmentCreate, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    shipment = create_shipment(db, request)
    if not shipment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order not found or already shipped")
    return shipment

@router.get("/shipments/{order_id}", response_model=ShipmentOut)
def get_order_shipment(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(user_required)):
    shipment = get_shippment(db, order_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment

@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
  
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, ENDPOINT_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    webhook_data = WebhookCreate(
        provider="stripe",
        event_id=event["id"],
        event_type=event["type"],
        payload=event
    )
    
    handle_webhook_event(db, webhook_data)

    return {"status": "received"}