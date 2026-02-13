from sqlalchemy.orm import Session, joinedload
from src.products.models import Category, Product, ProductImage
from src.products.schemas import (
    CategoryCreate,
    CategoryUpdate,
    ProductCreate,
    ProductUpdate,
    ProductImageCreate,
    ProductImageEdit,
)


def get_list_of_categories(db: Session):
    return db.query(Category).all()


def get_all_categories_with_products(db: Session):
    return db.query(Category).options(joinedload(Category.products)).all()


def get_single_category(db: Session, id: int):
    return (
        db.query(Category)
        .filter(Category.id == id)
        .options(joinedload(Category.products))
        .one()
    )


def create_category(db: Session, category: CategoryCreate):
    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(db: Session, id: int, category: CategoryUpdate):
    db_category = db.query(Category).filter(Category.id == id).first()

    if not db_category:
        return None

    for key, value in category.model_dump().items():
        setattr(db_category, key, value)

    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, id: int):
    db_category = db.query(Category).filter(Category.id == id).first()

    if not db_category:
        return None

    db.delete(db_category)
    db.commit()
    return db_category


def get_all_products(db: Session):
    return db.query(Product).options(joinedload(Product.images)).all()


def get_all_products_from_category(db: Session, category_id):
    return (
        db.query(Product)
        .options(joinedload(Product.images))
        .filter(Product.category_id == category_id)
        .all()
    )


def get_single_product(db: Session, product_id):
    return (
        db.query(Product)
        .options(joinedload(Product.images))
        .filter(Product.id == product_id)
        .one()
    )


def create_product(db: Session, new_product: ProductCreate):
    db_product = Product(**new_product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, updated_product: ProductUpdate):
    db_product = db.query(Product).filter(Product.id == product_id).one()
    if not db_product:
        return None

    for key, value in updated_product.model_dump().items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)

    return db_product


def delete_product(db: Session, product_id: int):
    db_product = db.query(Product).filter(Product.id == product_id).one()

    if not db_product:
        return None

    db.delete(db_product)
    db.commit()
    return db_product


def get_all_product_images_for_product(product_id: int, db: Session):
    return db.query(ProductImage).filter(ProductImage.product_id == product_id).all()


def delete_product_image(id: int, db: Session):
    db_image = db.query(ProductImage).filter(ProductImage.id == id).one()

    if not db_image:
        return None

    image_data = {"url": db_image.url}

    db.delete(db_image)
    db.commit()
    return image_data


def create_product_image(image: ProductImageCreate, db: Session):
    if image.is_main:
        db.query(ProductImage).filter(
            ProductImage.product_id == image.product_id
        ).update({"is_main": False})

    db_image = ProductImage(**image.model_dump())
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def edit_product_image(db: Session, image_id: int, image_data: ProductImageEdit):
    db_image = db.query(ProductImage).filter(ProductImage.id == image_id).first()

    if not db_image:
        return None

    if image_data.is_main:
        db.query(ProductImage).filter(
            ProductImage.product_id == db_image.product_id, ProductImage.id != image_id
        ).update({"is_main": False})

    db_image.is_main = image_data.is_main

    db.commit()
    db.refresh(db_image)
    return db_image
