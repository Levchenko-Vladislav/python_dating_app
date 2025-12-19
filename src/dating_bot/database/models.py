from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from .session import Base


class User(Base):
    """User model"""

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(String(100), unique=True, nullable=False)  # Telegram ID как строка
    username = Column(String(100), nullable=True)  # Telegram username с @
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    photo_id = Column(String(500))
    city = Column(String(100))
    goal = Column(String(20))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True, nullable=False)
    sex = Column(String(10))

    search_sex = Column(String(10), default="any")
    min_age = Column(Integer, default=18)
    max_age = Column(Integer, default=100)

    # Связи
    test_results = relationship("UserTestResult", back_populates="user", uselist=False)
    given_likes = relationship("Like", foreign_keys="Like.user_from_id", back_populates="user_from")
    received_likes = relationship("Like", foreign_keys="Like.user_to_id", back_populates="user_to")

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', telegram_id='{self.telegram_id}', username='{self.username}')>"


class UserTestResult(Base):
    """Результаты психологического теста пользователя"""

    __tablename__ = 'user_test_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)

    # Ответы на вопросы (в формате JSON: {question_id: answer_value})
    answers = Column(JSON, nullable=False)

    # Результаты по категориям (в формате JSON: {category: score})
    category_scores = Column(JSON, nullable=False)

    answered_count = Column(Integer, default=0)
    completed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_completed = Column(Boolean, default=False)

    user = relationship("User", back_populates="test_results")

    def __repr__(self):
        return f"<UserTestResult(user_id={self.user_id}, answered={self.answered_count}, completed={self.is_completed})>"


class Like(Base):
    """Лайки/дизлайки между пользователями"""

    __tablename__ = 'likes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_from_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Кто поставил
    user_to_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Кому поставил

    is_like = Column(Boolean, default=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user_from = relationship("User", foreign_keys=[user_from_id], back_populates="given_likes")
    user_to = relationship("User", foreign_keys=[user_to_id], back_populates="received_likes")

    def __repr__(self):
        action = "❤️" if self.is_like else "👎"
        return f"<Like({action} {self.user_from_id} → {self.user_to_id})>"


class Match(Base):
    """Взаимные лайки (мэтчи)"""

    __tablename__ = 'matches'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user1_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user2_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    matched_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    status = Column(String(20), default="active")

    user1 = relationship("User", foreign_keys=[user1_id])
    user2 = relationship("User", foreign_keys=[user2_id])

    def __repr__(self):
        return f"<Match({self.user1_id} ↔ {self.user2_id}, status={self.status})>"