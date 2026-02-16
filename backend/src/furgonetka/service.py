from fastapi import Header, BackgroundTasks
from sqlalchemy.orm import Session
from src.logistics.service import get_paid_shipments
from datetime import datetime as dt
from src.furgonetka.schemas import Tracking
from src.logistics.models import Shipment
from src.shopping.models import Order
from src.email.service import send_shipping_email
import os
from dotenv import load_dotenv

load_dotenv()


def get_orders(db: Session, authorization: str, datetime: str, limit: int = 100):
    if not authorization:
        return None

    if authorization != os.getenv("token"):
        return None

    datetime = dt.fromisoformat(datetime.replace("Z", "+00:00"))

    shipments = get_paid_shipments(db, datetime, limit)
    final_list = []
    for shipment in shipments:
        point_value = shipment.pickup_point_code if shipment.pickup_point_code else None
        comment_value = shipment.comment if shipment.comment else None
        company_value = shipment.company if shipment.company else None
        name = shipment.shipping_full_name.strip().split(maxsplit=1)[0]
        surname = shipment.shipping_full_name.strip().split(maxsplit=1)[1]
        surname = surname if surname else "---"

        products = []
        for item in shipment.order.items:
            products.append(
                {
                    "sourceProductId": item.product.id,
                    "name": item.product.name,
                    "priceGross": item.product.price,
                    "priceNet": round(float(item.product.price * 0.73, 2)),
                    "vat": 23,
                    "taxRate": 23,
                    "weight": item.product.weight / 1000,
                    "quantity": item.quantity,
                }
            )

        final_list.append(
            {
                "sourceOrderId": shipment.order.id,
                "sourceClientId": shipment.order.user_id,
                "datetimeOrder": shipment.order.created_at,
                "sourceDatetimeChange": shipment.order.updated_at,
                "service": shipment.courier.value,
                "serviceDescription": "Kurier " + shipment.courier.value,
                "status": shipment.order.status.value,
                "totalPrice": shipment.order.total_amount,
                "shippingCost": shipment.order.shipping_cost,
                "shippingMethodId": 12,
                "shippingTaxRate": 23,
                "totalPaid": shipment.order.total_amount,
                "codAmount": 0,
                "point": point_value,
                "comment": comment_value,
                "shippingAddress": {
                    "company": company_value,
                    "name": name,
                    "surname": surname,
                    "street": shipment.shipping_street,
                    "city": shipment.shipping_city,
                    "postcode": shipment.shipping_postal_code,
                    "countryCode": "PL",
                    "phone": shipment.shipping_phone,
                    "email": shipment.shipping_email,
                },
                "invoiceAddress": {
                    "company": company_value,
                    "name": name,
                    "surname": surname,
                    "street": shipment.shipping_street,
                    "city": shipment.shipping_city,
                    "postcode": shipment.shipping_postal_code,
                    "countryCode": "PL",
                    "phone": shipment.shipping_phone,
                    "email": shipment.shipping_email,
                    "nip": shipment.nip,
                },
                "products": products,
                "paymentDatetime": None,
            }
        )
    return final_list


def order_status(
    db: Session, authorization: str, id: int, number: str, courierService: str, background_task: BackgroundTasks
):
    if not authorization:
        return "401"

    if authorization != os.getenv("token"):
        return "401"

    order = db.query(Order).filter(Order.id == id).first()

    if not order:
        return None

    shipment = db.query(Shipment).filter(Shipment.order_id == order.id).first()
    if not shipment:
        return None

    shipment.tracking_number = number

    
    db.commit()
    db.refresh(shipment)
    background_task.add_task(send_shipping_email, order.id, number, shipment.courier.value, shipment.shipping_email)

    return shipment
