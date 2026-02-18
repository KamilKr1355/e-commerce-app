from fastapi import APIRouter, status, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from src.dependencies import get_db
from src.users.models import User
from typing import List, Optional
from src.shopping.schemas import GuestOrder
from src.shopping.service import create_guest_order
from src.auth.token import oauth2_scheme, get_current_user, get_optional_current_user
import jwt
import os
from src.shopping.schemas import (
    CartItemCreate, CartItemOut, CartOut, OrderOut, 
    Status, IncrementDecrement, Price, OrderStatus
)
from src.shopping.service import (
    get_cart_for_user, create_cart, delete_all_items_from_cart,
    decrease_quantity, delete_one_item_from_cart, change_order_status,
    create_order_from_cart, cancel_order, create_cart_item,
    total_price_of_cart, increase_quantity, get_order_by_id, get_users_orders,
)
from src.constants import user_required

router = APIRouter(tags=["shopping"], prefix="/shopping")

@router.get("/cart", response_model=CartOut)
def get_cart(db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_optional_current_user)):
    if not current_user:
        return {"id": 0, "user_id": 0, "items": []}
    
    cart = get_cart_for_user(db, current_user.id)
    if not cart:
        return {"id": 0, "user_id": current_user.id, "items": []}
    return cart

@router.post("/cart", response_model=CartOut)
def post_cart(db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_optional_current_user)):
    if not current_user:
        return {"id": 0, "user_id": 0, "items": []}
    
    new_cart = create_cart(db, current_user.id)
    return new_cart

@router.delete("/cart", response_model=Status)
def delete_everything_from_cart(db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_optional_current_user)):
    if not current_user:
        return {"status": "cleared_local"}
    
    delete_all_items_from_cart(db, current_user.id)
    return {"status": "deleted"}

@router.delete("/cart/{product_id}", response_model=Status)
def delete_single_item_from_cart(product_id: int, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_optional_current_user)):
    if not current_user:
        return {"status": "deleted_local"}
    
    delete_one_item_from_cart(db, product_id, current_user.id)
    return {"status": "deleted"}

@router.post("/cart/increase-quantity/{product_id}", response_model=CartItemOut)
def increment_quantity(request: IncrementDecrement, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_optional_current_user)):
    if not current_user:
        raise HTTPException(status_code=202, detail="Guest: handle in local storage")
    
    data = request.model_dump()
    product_id = data["product_id"]
    return increase_quantity(db, product_id, current_user.id)

@router.post("/cart/decrease-quantity/{product_id}", response_model=CartItemOut | Status)
def decrement_quantity(request: IncrementDecrement, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_optional_current_user)):
    if not current_user:
        raise HTTPException(status_code=202, detail="Guest: handle in local storage")
    
    data = request.model_dump()
    product_id = data["product_id"]
    return decrease_quantity(db, product_id, current_user.id)

@router.post("/cart/cartItem", response_model=CartItemOut)
def post_cart_item(request: CartItemCreate, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_optional_current_user)):
    if not current_user:
        raise HTTPException(status_code=202, detail="Guest: handle in local storage")
    
    return create_cart_item(db, request, user_id=current_user.id)

@router.get("/cart/price", response_model=Price)
def get_cart_price(db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_optional_current_user)):
    if not current_user:
        return {"total_price": 0.0}
    return total_price_of_cart(db, current_user.id)

@router.post("/order", response_model=OrderOut)
def post_order_from_cart(background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(user_required)):
    new_order = create_order_from_cart(db, current_user.id, background_tasks=background_tasks)
    if not new_order:
        raise HTTPException(status_code=404, detail="Error while placing order")
    return new_order

@router.post("/guest-order", response_model=OrderOut)
def post_guest_order(data: GuestOrder,background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    new_order = create_guest_order(db, data, background_tasks)
    if not new_order:
        raise HTTPException(status_code=404, detail="Error while placing order")
    return new_order

@router.get("/orders", response_model=List[OrderOut])
def get_all_orders(db: Session = Depends(get_db), current_user: User = Depends(user_required)):
    return get_users_orders(db, current_user.id)

@router.get("/order/{order_id}", response_model=OrderOut)
def get_specific_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(user_required)):
    order = get_order_by_id(db, order_id, current_user.id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.put("/order/{order_id}/status", response_model=OrderOut)
def change_status(order_id: int, request: OrderStatus, db: Session = Depends(get_db), current_user: User = Depends(user_required)):
    status_val = request.model_dump()["status"]
    return change_order_status(db, status_val, order_id, current_user.id)

@router.put("/order/{order_id}/cancel", response_model=OrderOut)
def deactivate_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(user_required)):
    return cancel_order(db, order_id, current_user.id)