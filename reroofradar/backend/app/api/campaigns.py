from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models.orm import User

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


@router.get("/")
def get_campaigns(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {"campaigns": [], "message": "No campaigns yet"}
