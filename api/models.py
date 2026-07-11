from pydantic import BaseModel
from typing import Dict, Any, Literal, List

class Geometry(BaseModel):
    geometry_type : Literal["Polygon", "MultiPolygon"]
    coordinates : List[Any]

class State(BaseModel):
    state_id : int
    name     : str
    capital  : str | None

class Municipality(BaseModel):
    name : str
    municipality_id : int