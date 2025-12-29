from pydantic import BaseModel
from typing import Optional


class RoleRightsSchema(BaseModel):
    read_posts_access: Optional[bool] = True
    write_posts_access: Optional[bool] = False
    delete_posts_access: Optional[bool] = False
    manage_roles_access: Optional[bool] = False
