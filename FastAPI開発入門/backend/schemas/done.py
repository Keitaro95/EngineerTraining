from pydantic import BaseModel

class DoneRespone(BaseModel):
    id: int

    class Config:
        orm_mode = True