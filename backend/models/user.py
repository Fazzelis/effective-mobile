from database.database import Base
from sqlalchemy import func, Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID


class User(Base):
    __tablename__ = "user"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    name = Column(String)
    surname = Column(String)
    patronymic = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)
