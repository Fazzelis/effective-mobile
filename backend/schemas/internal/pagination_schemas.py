from pydantic import BaseModel


class PaginationSchema(BaseModel):
    page: int
    page_size: int
    total_count: int
    total_pages: int
