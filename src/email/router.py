from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from src.email.schemas import Status, CodeCreate, CodeValidate
from src.dependencies import get_db
from src.email.service import send_register_code, validate_code
router = APIRouter(prefix="/email", tags=["email"])

@router.post("/register-code", response_model=Status, status_code=status.HTTP_201_CREATED)
def send_code(request: CodeCreate, db: Session = Depends(get_db)):
  status = send_register_code(db, receiver = request.models.dump()["email"])
  if not status:
    raise HTTPException(status_code=404)
  return status

@router.get("/register-code/validate", response_model=Status, status_code=status.HTTP_201_CREATED)
def validate_code(request: CodeValidate, db: Session = Depends(get_db)):
  status = validate_code(db=db, **request.model_dump())
  if not status:
    raise HTTPException(status_code=404)
  return status