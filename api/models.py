from pydantic import BaseModel
from typing import Dict, Any, Literal, List

class GeometryModel(BaseModel):
    type : Literal["Polygon", "MultiPolygon"]
    coordinates : Any

class StatePropertiesModel(BaseModel):
    state_id : int
    name     : str
    capital  : str | None

class MunicipalityPropertiesModel(BaseModel):
    municipality_db_id : int
    municipality_id    : int
    state_id           : int
    name               : str

class StateFeatureModel(BaseModel):
    type : Literal["Feature"]
    geometry : GeometryModel
    properties : StatePropertiesModel

class MunicipalityFeatureModel(BaseModel):
    type       : Literal["Feature"]
    geometry   : GeometryModel
    properties : MunicipalityPropertiesModel

class SectionFeatureModel(BaseModel):
    pass

class FeatureCollection(BaseModel):
    type : Literal["FeatureCollection"]
    features : List[StateFeatureModel] | List[MunicipalityFeatureModel]

