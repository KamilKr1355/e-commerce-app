from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.dependencies import get_db
from src.users.models import User
from src.constants import admin_required
from src.admin import service, schemas

router = APIRouter(prefix="/admin/stats", tags=["admin-stats"])

@router.get("/dashboard", response_model=schemas.DashboardStats)
def get_dashboard(
    db: Session = Depends(get_db), 
    current_user: User = Depends(admin_required)
):
    return service.get_admin_dashboard_stats(db)