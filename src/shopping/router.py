from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from src.dependencies import get_db
from src.users.models import User
from typing import List
from src.shopping.schemas import GuestOrder
from src.shopping.service import create_guest_order
from src.shopping.schemas import (
    CartBase,
    CartCreate,
    CartItemBase,
    CartItemCreate,
    CartItemOut,
    CartOut,
    OrderCreate,
    Status,
    IncrementDecrement,
    Price,
    OrderOut,
    OrderItemOut,
    OrderStatus,
)
from src.shopping.service import (
    get_cart_for_user,
    create_cart,
    delete_all_items_from_cart,
    decrease_quantity,
    delete_one_item_from_cart,
    change_order_status,
    create_order_from_cart,
    cancel_order,
    create_cart_item,
    total_price_of_cart,
    increase_quantity,
    get_order_by_id,
    get_users_orders,
)
from src.constants import allow_any, user_required, admin_required, superadmin_required

router = APIRouter(tags=["shopping"], prefix="/shopping")


@router.get(
    "/cart",
    response_model=CartOut,
    status_code=status.HTTP_200_OK,
    description="Returns user's cart",
)
def get_cart(
    db: Session = Depends(get_db), current_user: User = Depends(user_required)
):
    cart = get_cart_for_user(db, current_user.id)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User doesn't have cart"
        )

    return cart


@router.post(
    "/cart",
    response_model=CartOut,
    status_code=status.HTTP_201_CREATED,
    description="Creates user's cart",
)
def post_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):
    new_cart = create_cart(db, current_user.id)

    if not new_cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Error while creating a cart"
        )

    return new_cart


@router.delete(
    "/cart",
    response_model=Status,
    status_code=status.HTTP_200_OK,
    description="Deletes cart belonging to user",
)
def delete_everything_from_cart(
    db: Session = Depends(get_db), current_user: User = Depends(user_required)
):
    deleted_cart = delete_all_items_from_cart(db, current_user.id)

    if not deleted_cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User doesn't have cart"
        )

    return {"status": "deleted"}


@router.delete(
    "/cart/{product_id}",
    response_model=Status,
    status_code=status.HTTP_200_OK,
    description="Deletes item from cart",
)
def delete_single_item_from_cart(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):
    deleted_item = delete_all_items_from_cart(db, product_id, current_user.id)

    if not deleted_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User doesn't have that product in cart",
        )

    return {"status": "deleted"}


@router.post(
    "/cart/increase-quantity/{product_id}",
    response_model=CartItemOut,
    status_code=status.HTTP_202_ACCEPTED,
    description="Increases quantity of a product in cart",
)
def increment_quantity(
    request: IncrementDecrement,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):
    data = request.model_dump()
    product_id = data["product_id"]

    new_cart_item = increase_quantity(db, product_id, current_user.id)

    if not new_cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Error while incrementing"
        )

    return new_cart_item


@router.post(
    "/cart/decrease-quantity/{product_id}",
    response_model=CartItemOut | Status,
    status_code=status.HTTP_202_ACCEPTED,
    description="Decreases quantity of a product in cart",
)
def decrement_quantity(
    request: IncrementDecrement,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):
    data = request.model_dump()
    product_id = data["product_id"]
    new_cart_item = decrease_quantity(db, product_id, current_user.id)

    if not new_cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Error while incrementing"
        )

    return new_cart_item


@router.post(
    "/cart/cartItem",
    response_model=CartItemOut,
    status_code=status.HTTP_200_OK,
    description="Add item to a cart",
)
def post_cart_item(
    request: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):
    new_cart_item = create_cart_item(db, request, user_id=current_user.id)

    if not new_cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error while adding item to cart",
        )

    return new_cart_item


@router.get(
    "/cart/price",
    response_model=Price,
    status_code=status.HTTP_200_OK,
    description="Returns valaution of a cart",
)
def get_cart_price(
    db: Session = Depends(get_db), current_user: User = Depends(user_required)
):
    price = total_price_of_cart(db, current_user.id)
    if not price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Errow while evaluating"
        )

    return price


@router.post(
    "/order",
    response_model=OrderOut,
    status_code=status.HTTP_201_CREATED,
    description="Creates order from cart",
)
def post_order_from_cart(
    db: Session = Depends(get_db), current_user: User = Depends(user_required)
):

    new_order = create_order_from_cart(db, current_user.id)

    if not new_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Error while placing order"
        )

    return new_order


@router.post(
    "/order",
    response_model=OrderOut,
    status_code=status.HTTP_201_CREATED,
    description="Creates order from cart",
)
def post_guest_order(data: GuestOrder, db: Session = Depends(get_db)):

    new_order = create_guest_order(db, data)

    if not new_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Error while placing order"
        )

    return new_order


@router.get(
    "/orders",
    response_model=List[OrderOut],
    status_code=status.HTTP_200_OK,
    description="Returns all orders for specific user",
)
def get_all_orders(
    db: Session = Depends(get_db), current_user: User = Depends(user_required)
):
    orders = get_users_orders(db, current_user.id)
    if not orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Error while getting orders"
        )

    return orders


@router.get(
    "/order/{order_id}",
    response_model=OrderOut,
    status_code=status.HTTP_200_OK,
    description="Returns specific order",
)
def get_specific_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):
    order = get_order_by_id(db, order_id, current_user.id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Error while getting order id: {order_id} for user id: {current_user.id}",
        )

    return order


@router.put(
    "/order/{order_id}/status",
    response_model=OrderOut,
    status_code=status.HTTP_200_OK,
    description="Changes order's status",
)
def change_status(
    order_id: int,
    request: OrderStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):

    status = request.model_dump()["status"]
    changed_order = change_order_status(db, status, order_id, current_user.id)

    if not changed_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Error while changing status"
        )

    return changed_order


@router.put(
    "/order/{order_id}/cancel",
    response_model=OrderOut,
    status_code=status.HTTP_200_OK,
    description="Changes order's status to cancelled",
)
def deactivate_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):
    changed_order = cancel_order(db, order_id, current_user.id)

    if not changed_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Error while cancelling order"
        )

    return changed_order
