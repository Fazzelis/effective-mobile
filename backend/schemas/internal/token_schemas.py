from pydantic import BaseModel


class TokenInfoSchema(BaseModel):
    token: str
    token_type: str
