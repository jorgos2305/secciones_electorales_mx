from pydantic import BaseModel

class State(BaseModel):
    name     : str
    capital  : str | None