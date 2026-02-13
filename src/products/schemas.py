from pydantic import BaseModel
from typing import List, Optional

class BaseProduct(BaseModel):
  name: str
  description: Optional[str] = None
  price: float
  currency: Optional[str] = None
  stock : Optional[int] = None
  is_active: Optional[bool] = None
  category_id: int

class BaseImage(BaseModel):
  id: int
  product_id: int
  url: str
  is_main: Optional[bool] = None
  
class ImageOut(BaseImage):
  class Config:
    from_attributes = True

class ProductImageBase(BaseModel):
  product_id: int
  url: str
  is_main: Optional[bool] = False
  
class ProductImageOut(ProductImageBase):
  id: int
  
  class Config:
    from_attributes = True
    
class ProductOut(BaseProduct):
  id: int
  urls : Optional[List[ProductImageOut]] = []
  class Config:
        from_attributes = True
  
class ProductCreate(BaseProduct):
  class Config:
    from_attributes = True

class ProductUpdate(BaseProduct):
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
    
class ProductImageCreate(BaseModel):
  product_id: int
  url: str
  is_main: bool = False

  class Config:
      from_attributes = True
    
class ProductImageEdit(BaseModel):
  is_main: bool = False
  class Config:
    from_attributes = True