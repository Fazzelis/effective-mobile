from database.database import Base
from sqlalchemy import func, Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Role(Base):
    __tablename__ = "role"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    name = Column(String)
    rights_id = Column(UUID(as_uuid=True), ForeignKey("role_rights.id"))

    users = relationship("User", back_populates="role")
    rights = relationship("RoleRights", back_populates="role")
