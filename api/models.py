from pydantic import BaseModel
from typing import Dict, Any, Literal, List

class Geometry(BaseModel):
    type : Literal["Polygon", "MultiPolygon"]
    coordinates : List

class State(BaseModel):
    name     : str
    capital  : str | None
    geometry : Geometry