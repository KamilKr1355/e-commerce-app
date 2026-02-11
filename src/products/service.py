from sqlalchemy.orm import Session, joinedload
from src.products.models import Category
from src.products.schemas import CategoryCreate, CategoryUpdate

#categoryout
def get_list_of_categories(db: Session):
  return db.query(Category).all()
  
#categoryproductsout
def get_all_categories_with_products(db: Session):
  return db.query(Category).options(joinedload(Category.products)).all()

#categoryproductsout
def get_single_category(db: Session, id: int):
  return db.query(Category).filter(Category.id == id).options(joinedload(Category.products)).one()
  
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
  