from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from src.users.models import User
from src.dependencies import get_db
from src.products.schemas import (
    CategoryOut,
    CategoryUpdate,
    CategoryProductsOut,
    CategoryCreate,
    StatusResponse,
    ProductOut,
    ProductCreate,
    ProductUpdate,
    ProductImageCreate,
    ProductImageEdit,
    ProductImageOut,
    DiscountCreate,
    DiscountOut,
)
from src.products.service import (
    get_list_of_categories,
    get_all_categories_with_products,
    get_single_category,
    create_category,
    update_category,
    delete_category,
    get_all_products,
    get_all_products_from_category,
    get_single_product,
    create_product,
    update_product,
    delete_product,
    get_all_product_images_for_product,
    delete_product_image,
    create_product_image,
    edit_product_image,
    add_discount,
    cancel_discount,
)
from src.constants import user_required, admin_required, superadmin_required, allow_any
from typing import List
import shutil
import os

UPLOAD_DIR = "static/product_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)
router = APIRouter(prefix="/shop", tags=["products"])


@router.get(
    "/categories",
    response_model=List[CategoryOut],
    status_code=status.HTTP_200_OK,
    description="Returns list of categories (without products assigned) ",
)
def get_categories(
    db: Session = Depends(get_db), current_user: User = Depends(allow_any)
):
    categories = get_list_of_categories(db)

    if not categories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categories don't exist"
        )

    return categories


@router.get(
    "/categories-products",
    response_model=List[CategoryProductsOut],
    status_code=status.HTTP_200_OK,
    description="Returns list of categories including products assigned",
)
def get_categories_products(
    db: Session = Depends(get_db), current_user: User = Depends(allow_any)
):
    categories_products = get_all_categories_with_products(db)

    if not categories_products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categories don't exist"
        )

    return categories_products


@router.get(
    "/categories/{category_id}",
    response_model=CategoryProductsOut,
    status_code=status.HTTP_200_OK,
    description="Returns single category with products assigned",
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(allow_any),
):
    category = get_single_category(db, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} doesn't exist",
        )

    return category


@router.post(
    "/categories",
    response_model=CategoryOut,
    status_code=status.HTTP_201_CREATED,
    description="Endpoint for creating category",
)
def post_category(
    request: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    new_category = create_category(db, request)

    if not new_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong creating category",
        )

    return new_category


@router.put(
    "/categories/{category_id}",
    response_model=CategoryOut,
    status_code=status.HTTP_200_OK,
    description="Endpoint for editing category",
)
def put_category(
    category_id: int,
    request: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    edited_category = update_category(db, category_id, request)

    if not edited_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    return edited_category


@router.delete(
    "/categories/{category_id}",
    response_model=StatusResponse,
    description="Endpoint for deleting category",
)
def del_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):

    deleted = delete_category(db, category_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    return {"status": "deleted"}


@router.get(
    "/products",
    response_model=List[ProductOut],
    status_code=status.HTTP_200_OK,
    description="Returns every single product in db",
)
def get_every_product(
    db: Session = Depends(get_db), current_user: User = Depends(allow_any)
):
    products = get_all_products(db)

    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="There are no products"
        )

    return products


@router.get(
    "/products/{category_id}",
    response_model=List[ProductOut],
    status_code=status.HTTP_200_OK,
)
def get_every_product_from_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(allow_any),
):
    products = get_all_products_from_category(db, category_id)

    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="There are no products"
        )

    return products


@router.get(
    "/product/{product_id}", response_model=ProductOut, status_code=status.HTTP_200_OK
)
def get_one_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(allow_any),
):
    product = get_single_product(db, product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no product with id {product_id}",
        )

    product.views += 1
    db.commit()

    return product


@router.post("/product", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def post_product(
    request: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    new_product = create_product(db, request)

    if not new_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Didn't manage to create a product",
        )

    return new_product


@router.put(
    "/product/{product_id}", response_model=ProductOut, status_code=status.HTTP_200_OK
)
def edit_product(
    product_id: int,
    request: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    edited_product = update_product(db, product_id, request)

    if not edited_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Didn't manage to update a product",
        )

    if isinstance(edited_product, dict) and edited_product["error"] == "lower_price":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="If you want to lower price, use discount",
        )

    return edited_product


@router.delete(
    "/product/{product_id}",
    response_model=StatusResponse,
    status_code=status.HTTP_200_OK,
    description="Deletes a specific product",
)
def del_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    deleted_product = delete_product(db, product_id)

    if not deleted_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Didn't manage to delete a product",
        )

    return {"status": "deleted"}


@router.get(
    "/product/{product_id}/images",
    response_model=List[ProductImageOut],
    status_code=status.HTTP_200_OK,
    description="Returns all images for product",
)
def get_every_product_image(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(allow_any),
):
    images = get_all_product_images_for_product(product_id, db)

    if not images:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="There are no products images"
        )

    return images


@router.delete(
    "/image/{image_id}",
    response_model=StatusResponse,
    status_code=status.HTTP_200_OK,
    description="Deletes a specific image",
)
def del_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    deleted_image_data = delete_product_image(image_id, db)

    if not deleted_image_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image not found in database"
        )

    file_path = deleted_image_data["url"].lstrip("/")

    if os.path.exists(file_path):
        os.remove(file_path)

    return {"status": "deleted"}


@router.post(
    "/product/{product_id}/upload-image",
    response_model=ProductImageOut,
    status_code=status.HTTP_201_CREATED,
)
def post_image(
    product_id: int,
    is_main: bool = Form(False),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    file_name = f"{product_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    web_url = f"/{file_path}".replace("\\", "/")

    new_image_data = ProductImageCreate(
        product_id=product_id, url=web_url, is_main=is_main
    )

    return create_product_image(new_image_data, db)


@router.put(
    "/image/{image_id}", response_model=ProductImageOut, status_code=status.HTTP_200_OK
)
def edit_image(
    image_id: int,
    request: ProductImageEdit,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    edited_image = edit_product_image(db, image_id, request)

    if not edited_image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Didn't manage to update an image",
        )

    return edited_image


@router.post(
    "/product/{product_id}/discount",
    response_model=DiscountOut,
    status_code=status.HTTP_201_CREATED,
    description="Creates discount",
)
def post_discount(
    product_id: int,
    discount_data: DiscountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    new_discount = add_discount(db, product_id, **discount_data.model_dump())

    if not new_discount:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error while creating a discount",
        )

    return new_discount


@router.delete(
    "/product/{product_id}/discount",
    response_model=StatusResponse,
    description="Endpoint for deleting discount",
)
def del_discount(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):

    deleted = cancel_discount(db, product_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Discount not found"
        )

    return {"status": "deleted"}
