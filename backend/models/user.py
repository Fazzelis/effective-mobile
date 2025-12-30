from database.database import Base
from sqlalchemy import func, Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "user"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    name = Column(String)
    surname = Column(String)
    patronymic = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)

    role_id = Column(UUID(as_uuid=True), ForeignKey("role.id"))

    role = relationship("Role", back_populates="users")
    posts = relationship("Post", back_populates="author")
