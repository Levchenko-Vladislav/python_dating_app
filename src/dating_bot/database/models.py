from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime, timezone

from .session import Base

class User(Base):
    """User model"""

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    photo_id = Column(String(500))
    city = Column(String(100))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True, nullable=False)
    sex = Column(String(10))

    search_sex = Column(String(10), default="any")
    min_age = Column(Integer, default=18)
    max_age = Column(Integer, default=100)

    def __repr__(self):
        return f"<User(id = {self.id}, name = '{self.name}', telegram_id = {self.telegram_id})>"