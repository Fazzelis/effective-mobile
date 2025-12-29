from database.database import Base
from sqlalchemy import func, Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Post(Base):
    __tablename__ = "post"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    title = Column(String)
    text = Column(String)
    author_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))

    author = relationship("User", back_populates="posts")
