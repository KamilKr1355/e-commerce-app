import os 
import stripe
from dotenv import load_dotenv
from src.shopping.models import Order, OrderItem
from src.products.models import Product
from sqlalchemy.orm import Session, joinedload

load_dotenv()
stripe.api_key = os.getenv("sk_stripe")

def create_checkout_session(db: Session, order: Order):
  try:
    data = db.query(Order).options(joinedload(Order.items).joinedload(OrderItem.product)).filter(Order.id == order.id).first()
    if not data:
            return {"error": "Order not found"}
    line_items = []
    for item in data.items:
      line_item = {'price_data': {
                    'currency': item.product.currency.lower(),
                    'product_data': {
                      'name': item.product_name_snapshot
                    },
                    'unit_amount': int(item.price * 100),
                  },
                   'quantity': item.quantity,
                   }
      line_items.append(line_item)
    session = stripe.checkout.Session.create(
      line_items=line_items,
      mode='payment',
      success_url='http://localhost:8000/success',
      cancel_url='http://localhost:8000/cancel',
      client_reference_id=str(data.id),
      metadata={"order_id": data.id}
    )
    return session.url, session.id
  except Exception as e:
    return None, None
    