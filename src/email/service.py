from sqlalchemy.orm import Session
from email.message import Message
from src.users.models import RegistrationCode
from datetime import datetime, timedelta
import random
import smtplib
from email.message import EmailMessage
from src.shopping.models import Order
import os
from dotenv import load_dotenv
import random
import logging

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")


logger = logging.getLogger(__name__)

def send_email(subject: str, receiver: str, content: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = receiver
    msg.set_content(content)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)
        return True
    except Exception as e:
        logger.error(f"Error in sending email to {receiver}: {e}")
        return False

def send_register_code(db: Session, email: str):
    code = "".join(random.choices([chr(i) for i in range(65, 91)], k=5))
    
    db.query(RegistrationCode).filter(RegistrationCode.email == email).delete()
    

    new_code = RegistrationCode(
        email=email, 
        code=code, 
        expires_at=datetime.now() + timedelta(minutes=30)
    )
    db.add(new_code)
    db.commit()

    content = f"Witaj!\n\nTwój kod weryfikacyjny to: {code}\nKod wygaśnie za 30 minut."
    send_email("Weryfikacja konta", email, content)

    return {"status":"ok"}

def validate_code(db: Session, code: str, receiver: str):
  registration_code = db.query(RegistrationCode).filter(RegistrationCode.email == receiver).first()
  if code == registration_code.code:
    return {"status":"ok"}
  
  return None

def delete_too_old(db: Session, time: int):
  time_limit = datetime.now() - timedelta(seconds=time)
  codes_list = db.query(RegistrationCode).filter(RegistrationCode.created_at < time_limit).all()
  
  if codes_list:
    for code in codes_list:
      db.delete(code)
      
  db.commit()
  
def send_order_confirmation(order: Order, email: str):
    items_list = "\n".join([f"- {i.product_name_snapshot} x{i.quantity}: {i.price} PLN" for i in order.items])
    content = f"""
    Potwierdzamy otrzymanie zamówienia nr {order.id}!
    
    Twoje zakupy:
    {items_list}
    
    Suma: {order.total_amount} {order.currency}
    
    Dostawa: {order.shipment.shipping_street}, {order.shipment.shipping_city}
    
    Czekamy na zaksięgowanie płatności.
    """
    return send_email(f"Potwierdzenie zamówienia nr {order.id}", email, content)

def send_payment_success_email(order_id: int, email: str):
    content = f"""
    Otrzymaliśmy płatność za zamówienie nr {order_id}.
    Twoje zamówienie trafiło do realizacji. Poinformujemy Cię, gdy przesyłka wyruszy w drogę!
    """
    return send_email(f"Płatność za zamówienie {order_id} przyjęta", email, content)

def send_shipping_email(order_id: int, tracking_number: str, courier: str, email: str):
    content = f"""
    Twoje zamówienie nr {order_id} zostało wysłane!
    
    Przewoźnik: {courier}
    Numer śledzenia: {tracking_number}
    
    Możesz śledzić paczkę na stronie kuriera.
    """
    return send_email(f"Zamówienie nr {order_id} wysłane", email, content)

def send_order_cancelled_email(order_id: int, email: str):
    content = f"""
    Zamówienie nr {order_id} zostało anulowane z powodu braku płatności w wymaganym czasie.
    Jeśli nadal chcesz dokonać zakupu, prosimy o złożenie nowego zamówienia.
    """
    return send_email(f"Zamówienie nr {order_id} zostało anulowane", email, content)