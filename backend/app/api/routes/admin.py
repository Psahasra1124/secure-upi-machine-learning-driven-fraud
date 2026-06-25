from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import AdminUser, DbSession
from app.models import User
from app.schemas.auth import UserRead

router = APIRouter(prefix="/admin", tags=["Administration"])


@router.get("/users", response_model=list[UserRead])
def list_users(db: DbSession, _: AdminUser) -> list[User]:
    return list(db.scalars(select(User).order_by(User.created_at.desc())).all())

