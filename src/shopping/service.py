from fastapi import BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta
from src.users.models import User
from src.shopping.models import Cart, CartItem, Order, OrderItem
from src.products.models import Product
from src.shopping.schemas import CartCreate, CartItemCreate
from src.shopping.constants import OrderStatus
from src.users.constants import Role
from src.shopping.schemas import GuestOrder
from src.logistics.models import Shipment
from src.email.service import send_order_confirmation, send_order_cancelled_email



def get_cart_for_user(db: Session, user_id: int):
    return (
        db.query(Cart)
        .options(joinedload(Cart.items).joinedload(CartItem.product))
        .filter(Cart.user_id == user_id)
        .first()
    )


def create_cart(db: Session, user_id: int):
    existing_cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if existing_cart:
        return None

    created_cart = Cart(user_id=user_id)

    db.add(created_cart)
    db.commit()
    db.refresh(created_cart)

    return created_cart


def delete_all_items_from_cart(db: Session, user_id: int):
    db_cart = get_cart_for_user(db, user_id)

    if not db_cart:
        return None

    db_cart.items.clear()
    db.commit()
    db.refresh(db_cart)

    return db_cart


def delete_one_item_from_cart(db: Session, product_id: int, user_id: int):
    cart_item = (
        db.query(CartItem)
        .join(Cart)
        .filter(Cart.user_id == user_id, CartItem.product_id == product_id)
        .options(joinedload(CartItem.product))
        .first()
    )
    if not cart_item:
        return None
    db.delete(cart_item)
    db.commit()

    return cart_item


def increase_quantity(db: Session, product_id: int, user_id: int):
    cart_item = (
        db.query(CartItem)
        .join(Cart)
        .filter(Cart.user_id == user_id, CartItem.product_id == product_id)
        .options(joinedload(CartItem.product))
        .first()
    )
    if not cart_item:
        return None
    if cart_item.quantity < cart_item.product.stock:
        cart_item.quantity += 1
    else:
        return None

    db.commit()
    db.refresh(cart_item)
    return cart_item


def decrease_quantity(db: Session, product_id: int, user_id: int):
    cart_item = (
        db.query(CartItem)
        .join(Cart)
        .filter(Cart.user_id == user_id, CartItem.product_id == product_id)
        .options(joinedload(CartItem.product))
        .first()
    )
    if not cart_item:
        return None

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
    else:
        delete_one_item_from_cart(db, product_id, user_id)
        return {"status": "deleted"}

    db.commit()
    db.refresh(cart_item)
    return cart_item


def create_cart_item(db: Session, cart_item: CartItemCreate, user_id: int):
    data = cart_item.model_dump()
    existing_cart = (
        db.query(CartItem)
        .filter(
            CartItem.product_id == data["product_id"],
            CartItem.cart_id == data["cart_id"],
        )
        .first()
    )
    product_id = data["product_id"]
    if existing_cart:
        return increase_quantity(db, product_id, user_id)

    new_cart_item = CartItem(**data)
    product = db.query(Product).filter(Product.id == new_cart_item.product_id).first()
    if not product:
        return None

    price = product.current_price
    new_cart_item.price_at_time = price

    db.add(new_cart_item)
    db.commit()
    db.refresh(new_cart_item)

    return new_cart_item


def total_price_of_cart(db: Session, user_id: int):
    cart = get_cart_for_user(db, user_id)
    if not cart:
        return 0
    summed = sum(item.price_at_time * item.quantity for item in cart.items)
    return {"total_price": summed}


def create_order_from_cart(db: Session, user_id: int, background_tasks: BackgroundTasks):
    cart = get_cart_for_user(db, user_id)
    if not cart or not cart.items:
        return None

    total_amount = sum(item.product.price * item.quantity for item in cart.items)

    new_order = Order(
        user_id=user_id,
        status=OrderStatus.pending,
        total_amount=total_amount,
        currency="PLN",
    )

    db.add(new_order)
    db.flush()

    for cart_item in cart.items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=cart_item.product.id,
            product_name_snapshot=cart_item.product.name,
            price=cart_item.product.price,
            quantity=cart_item.quantity,
        )
        db.add(order_item)

        if cart_item.product.stock >= cart_item.quantity:
            cart_item.product.stock -= cart_item.quantity
        else:
            db.rollback()
            return None

    cart.items.clear()
    background_tasks.add_task(send_order_confirmation, new_order, new_order.shipment.shipping_email)

    db.commit()
    db.refresh(new_order)
    return new_order


def get_users_orders(db: Session, user_id: int):
    return (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .all()
    )


def get_order_by_id(db: Session, order_id: int, user_id: int):
    return (
        db.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
        .filter(Order.id == order_id, Order.user_id == user_id)
        .first()
    )


def cancel_order(db: Session, order_id: int, user_id: int):
    db_order = (
        db.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
        .filter(Order.id == order_id)
        .first()
    )
    if not db_order:
        return None

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    is_owner = db_order.user_id == user.id
    is_admin = user.role in [Role.admin, Role.superadmin]
    if not (is_owner or is_admin) or db_order.status != OrderStatus.pending:
        return None

    for item in db_order.items:
        if item.product:
            item.product.stock += item.quantity

    db_order.status = OrderStatus.cancelled
    db.commit()
    db.refresh(db_order)
    return db_order

def cancel_pending_orders(db: Session, time: int):
    expired_limit = datetime.now() - timedelta(seconds=time)
    db_orders = (
        db.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
        .filter(Order.status == OrderStatus.pending,
                Order.created_at < expired_limit)
        .all()
    )
    if not db_orders:
        return None

    for order in db_orders:
        send_order_cancelled_email(order.id, order.shipment.shipping_email)
        for item in order.items:
            if item.product:
                item.product.stock += item.quantity

        order.status = OrderStatus.cancelled
    db.commit()
    return {"status":"cancelled"}
def change_order_status(
    db: Session, new_status: OrderStatus, order_id: int, user_id: int
):
    if new_status == OrderStatus.cancelled:
        return cancel_order(db, order_id, user_id)
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        return None

    db_order.status = new_status
    db.commit()
    db.refresh(db_order)
    return db_order


def create_guest_order(db: Session, data: GuestOrder):
    if not data.items:
        return None

    total_price = 0
    list_items = []
    for item in data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not (product and item.quantity <= product.stock):
            return None
        order_item = OrderItem(
            product_id=product.id,
            product_name_snapshot=product.name,
            product_price=product.price,
            quantity=item.quantity,
        )
        list_items.append(order_item)
        total_price += product.price * item.quantity
        product.stock -= item.quantity

    new_order = Order(
        contact_email=data.email,
        status=OrderStatus.pending,
        total_amount=total_price,
    )

    db.add(new_order)
    db.flush()

    for order_item in list_items:
        order_item.order_id = new_order.id
        db.add(order_item)

    new_shipment = Shipment(**data.shipping_data.model_dump())
    db.add(new_shipment)

    db.commit()
    db.refresh(new_order)
    return new_order
