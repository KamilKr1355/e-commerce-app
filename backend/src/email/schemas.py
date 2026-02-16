from pydantic import BaseModel, EmailStr

class Status(BaseModel):
  status: str
  
class CodeCreate(BaseModel):
  email: EmailStr
  
class CodeValidate(BaseModel):
  code: str
  receiver: str
  