from database.database import Base
from sqlalchemy import func, Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class RoleRights(Base):
    __tablename__ = "role_rights"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    read_access = Column(Boolean)
    write_access = Column(Boolean)
    delete_access = Column(Boolean)
    role_id = Column(UUID(as_uuid=True), ForeignKey("role.id"))

    role = relationship("Role", back_populates="rights")
