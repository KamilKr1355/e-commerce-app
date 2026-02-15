from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload
from src.users.models import User
from src.shopping.models import Order, OrderItem, OrderStatus
from src.auth.hasher import get_password_hash, verify_password
from src.users.constants import Role


def count_users(db: Session):
    return db.execute(func.count(User).select(User)).first()


def get_limitted_users_list(db: Session, offset: int = 0, limit: int = 50):
    paginated_list = db.execute(select(User).offset(offset).limit(limit)).all()
    users_count = count_users()
    additional_page = 1 if (users_count - (users_count // limit) * limit) > 0 else 0
    total_pages = users_count // limit + additional_page

    return {
        "items": paginated_list,
        "total": users_count,
        "offset": offset,
        "limit": limit,
        "total_pages": total_pages,
    }


def ban_user(db: Session, email: str, current_user: User):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None

    allow_ban_admin = current_user.role == Role.superadmin
    allow_ban_user = (
        current_user.role == Role.superadmin or current_user.role == Role.admin
    )

    allowed = True
    match user.role:
        case Role.admin:
            allowed = False if not allow_ban_admin else True
        case Role.user:
            allowed = False if not allow_ban_user else True
        case Role.superadmin:
            return None
        case _:
            return None
    if not allowed:
        return None

    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


def user_details(db: Session, email: str):
    user = (
        db.query(User)
        .options(joinedload(User.orders).joinedload(Order.items))
        .filter(User.email == email)
        .first()
    )
    if user:
        return None

    return user


def my_account_detail(db: Session, user_id: int):
    user = (
        db.query(User)
        .options(joinedload(User.orders).joinedload(Order.items))
        .filter(User.id == user_id)
        .first()
    )
    if not user:
        return None

    return user


def change_password(
    db: Session, user_id: int, current_password: str, new_password: str
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    old_password_hashed = user.hashed_password
    if verify_password(current_password, old_password_hashed):
        user.hashed_password = get_password_hash(new_password)

    db.commit()
    db.refresh(user)

    return user


def change_role(db: Session, email: str, current_user: User, upgrade: bool):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None

    allow = current_user.role == Role.superadmin

    if not allow:
        return None

    if upgrade and user.role == Role.user:
        user.role = Role.admin
    elif not upgrade and user.role == Role.admin:
        user.role = Role.user
    else:
        return None
    db.commit()
    db.refresh(user)
    return user


def upgrade_user(db: Session, email: str, current_user: User):
    return change_role(db,email, current_user, True)


def downgrade_user(db: Session, email: str, current_user: User):
    return change_role(db,email, current_user, False)
