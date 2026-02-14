from fastapi import APIRouter, Header, Depends, Request, status, HTTPException, Response
from src.dependencies import get_db
from sqlalchemy.orm import Session
from src.furgonetka.service import get_orders, order_status
from src.furgonetka.schemas import Tracking, TrackingInfo, FurgonetkaWebhookPayload
import os
import hashlib
import datetime
from src.logistics.constants import Status as ShipmentStatus
from src.logistics.models import Shipment
from src.shopping.models import Order
from src.shopping.constants import OrderStatus
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/furgonetka", tags=["furgonetka"])


@router.get("/orders", status_code=status.HTTP_200_OK)
def get_every_order(
    request: Request, datetime: str, limit: int, db: Session = Depends(get_db)
):
    header = request.headers.get("Authorization")
    orders = get_orders(db, header, datetime, limit)

    if not orders:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return Response(status_code=status.HTTP_200_OK)


@router.post("/orders/{id}/tracking_number", status_code=status.HTTP_200_OK)
def order_tracking(request: Tracking, id: int, db: Session = Depends(get_db)):
    header = request.headers.get("Authorization")
    shipment = order_status(db=db, authorization=header, id=id, **request.model_dump())

    if shipment == "401":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    elif not shipment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return Response(status_code=status.HTTP_200_OK)
  
@router.post("/webhooks/furgonetka")
async def furgonetka_webhook(payload: FurgonetkaWebhookPayload, db: Session = Depends(get_db)):
    salt = os.getenv("FURGONETKA_WEBHOOK_SALT")
    control_string = (
        str(payload.package_id) +
        payload.package_no +
        payload.partner_order_id +
        payload.tracking.state +
        payload.tracking.description +
        payload.tracking.datetime +
        payload.tracking.branch +
        salt
    )
    
    calculated_control = hashlib.md5(control_string.encode('utf-8')).hexdigest()

    if payload.control != calculated_control:
        return {"status": "ERROR"}

    order_id = int(payload.partner_order_id)
    shipment = db.query(Shipment).filter(Shipment.order_id == order_id).first()

    if shipment:
        f_state = payload.tracking.state
        
        if f_state == "delivered":
            shipment.status = ShipmentStatus.success
            shipment.delivered_at = datetime.now()
            order = db.query(Order).filter(Order.id == order_id).first()
            if order:
                order.status = OrderStatus.completed
        
        elif f_state in ["sent", "shipped", "out_for_delivery"]:
            shipment.status = ShipmentStatus.pending
            if not shipment.shipped_at:
                shipment.shipped_at = datetime.now()

        elif f_state in ["returned", "delivery_error"]:
            shipment.status = ShipmentStatus.failed

        db.commit()

    
    return {"status": "OK"}