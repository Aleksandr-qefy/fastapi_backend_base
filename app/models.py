from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UUID
import uuid

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=False)
    nickname = Column(String, unique=True, nullable=False, index=False)
    hashed_password = Column(String, nullable=False)


class UserUnconfirmed(Base):
    __tablename__ = "usersunconfirmed"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=False, nullable=False, index=False)
    nickname = Column(String, unique=False, nullable=False, index=False)
    hashed_password = Column(String, nullable=False)
