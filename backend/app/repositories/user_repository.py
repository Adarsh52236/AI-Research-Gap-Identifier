from typing import Optional, List
import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, user_in: UserCreate, password_hash: str) -> User:
        db_user = User(
            full_name=user_in.full_name,
            email=user_in.email,
            username=user_in.username,
            password_hash=password_hash
        )
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user

    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None))
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email, User.deleted_at.is_(None))
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username, User.deleted_at.is_(None))
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def update(self, user_id: uuid.UUID, user_in: UserUpdate, password_hash: Optional[str] = None) -> Optional[User]:
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None
            
        update_data = user_in.model_dump(exclude_unset=True)
        if 'password' in update_data:
            del update_data['password']
            
        if password_hash:
            update_data['password_hash'] = password_hash
            
        for field, value in update_data.items():
            setattr(db_user, field, value)
            
        self.session.commit()
        self.session.refresh(db_user)
        return db_user

    def soft_delete(self, user_id: uuid.UUID) -> bool:
        db_user = self.get_by_id(user_id)
        if not db_user:
            return False
            
        db_user.deleted_at = datetime.now(timezone.utc)
        self.session.commit()
        return True
