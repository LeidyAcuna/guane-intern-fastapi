from uuid import uuid4
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .db import Base


class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    name = Column(String)
    lastname = Column(String)
    email = Column(String, unique=True, index=True)

    dogs = relationship("Dog", back_populates="user")


class Dog(Base):
    __tablename__ = "dog"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    name = Column(String)
    picture = Column(String)
    create_date = Column(String)
    is_adopted = Column(Boolean)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))

    user = relationship("User", back_populates="dogs")
