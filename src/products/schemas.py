from pydantic import BaseModel
from typing import List, Optional

class BaseProduct(BaseModel):
  id: int
  name: str
  description: str
  price: float
  currency: Optional[str] = None

class ProductOut(BaseProduct):
  is_active: bool

  class Config:
        from_attributes = True
  
class BaseCategory(BaseModel):
  name: str
  slug: str
  parent_id: Optional[int] = None

class CategoryProductsOut(BaseCategory):
  id: int
  products: List[ProductOut]
  
  class Config:
        from_attributes = True
        
class CategoryOut(BaseCategory): 
  id: int 
  class Config:
        from_attributes = True
        
class CategoryCreate(BaseCategory):
  pass

class CategoryUpdate(BaseCategory):
  pass

class StatusResponse(BaseModel):
  status: str