from database.database import Base
from sqlalchemy import func, Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Role(Base):
    __tablename__ = "role"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    name = Column(String)
    read_posts_access = Column(Boolean)
    write_posts_access = Column(Boolean)
    delete_posts_access = Column(Boolean)
    manage_roles_access = Column(Boolean)

    users = relationship("User", back_populates="role")
