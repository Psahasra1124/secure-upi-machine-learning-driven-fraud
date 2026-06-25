from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import Base, SessionLocal, engine
from app.models import User


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        admin = db.scalar(select(User).where(User.email == settings.admin_email.lower()))
        if admin is None:
            db.add(
                User(
                    full_name="Secure UPI Administrator",
                    email=settings.admin_email.lower(),
                    hashed_password=get_password_hash(settings.admin_password),
                    role="admin",
                    is_active=True,
                )
            )
            try:
                db.commit()
            except IntegrityError:
                # Multiple API workers may bootstrap simultaneously. A competing
                # worker creating the same unique email is a successful outcome.
                db.rollback()
