from pydantic import BaseModel
from uuid import UUID


class ItemDeleteResponse(BaseModel):
    item_id: UUID
    row_count: int
