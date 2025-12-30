from pydantic import BaseModel


class PostRequestSchema(BaseModel):
    title: str
    text: str
