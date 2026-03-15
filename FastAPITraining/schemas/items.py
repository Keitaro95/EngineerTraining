from pydantic import BaseModel, ConfigDict

class ResponseItem(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    tax: float = 10.5
    