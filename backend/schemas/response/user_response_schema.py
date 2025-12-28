from pydantic import BaseModel
from uuid import UUID
from schemas.internal.token_schemas import TokenInfoSchema


class UserAuthSchema(BaseModel):
    user_id: UUID
    token_info: TokenInfoSchema
