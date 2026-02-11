from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.dependencies import get_db
from src.products.schemas import CategoryOut, CategoryUpdate, CategoryProductsOut, CategoryCreate, StatusResponse
from src.products.service import get_list_of_categories, get_all_categories_with_products, get_single_category,create_category, update_category, delete_category
from src.constants import user_required, admin_required, superadmin_required, allow_any
from typing import List

router = APIRouter(prefix="/shop", tags=["products"])

@router.get("/categories", response_model=List[CategoryOut], status_code=status.HTTP_200_OK, description="Returns list of categories (without products assigned) ")
def get_categories(db: Session = Depends(get_db), current_user = Depends(allow_any)):
  categories = get_list_of_categories(db)
  
  if not categories:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Categories don't exist")
  
  return categories

@router.get("/categories-products", response_model=List[CategoryProductsOut], status_code=status.HTTP_200_OK, description="Returns list of categories including products assigned")
def get_categories_products(db: Session = Depends(get_db), current_user = Depends(allow_any)):
  categories_products = get_all_categories_with_products(db)
  
  if not categories_products:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categories don't exist")
  
  return categories_products

@router.get("/categories/{category_id}", response_model=CategoryProductsOut, status_code=status.HTTP_200_OK, description="Returns single category with products assigned")
def get_category(category_id: int, db: Session = Depends(get_db), current_user = Depends(allow_any)):
  category = get_single_category(db, category_id)
  
  if not category:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category with id {category_id} doesn't exist")
  
  return category

@router.post("/categories", response_model=CategoryOut, status_code=status.HTTP_201_CREATED, description="Endpoint for creating category")
def post_category(request: CategoryCreate, db: Session = Depends(get_db), current_user = Depends(admin_required)):
  new_category = create_category(db, request)
  
  if not new_category:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something went wrong creating category")
    
  return new_category

@router.put("/categories/{category_id}", response_model=CategoryOut, status_code=status.HTTP_200_OK, description="Endpoint for editing category")
def put_category(category_id: int, request: CategoryUpdate, db: Session = Depends(get_db), current_user = Depends(admin_required)):
  edited_category = update_category(db, category_id, request)
  
  if not edited_category:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
  
  return edited_category
  
@router.delete("/categories/{category_id}", response_model=StatusResponse, description="Endpoint for deleting category")
def del_category(category_id: int, db: Session = Depends(get_db), current_user = Depends(admin_required)):
  
  deleted = delete_category(db, category_id)
  
  if not deleted:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
  
  return {"status": "deleted"}