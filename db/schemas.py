from typing import TypedDict, Tuple, List, Literal, Any

class Geometry(TypedDict):
    type        : Literal["Polygon", "MultiPolygon"]
    coordinates : Any

class StateProperties(TypedDict):
    state_id : int
    name     : str
    capital  : str | None

class MunicipalityProperties(TypedDict):
    municipality_db_id : int
    municipality_id    : int
    state_id           : int
    name               : str

class StateFeature(TypedDict):
    type       : Literal["Feature"]
    geometry   : Geometry
    properties : StateProperties

class MunicipalityFeature(TypedDict):
    type       : Literal["Feature"]
    geometry   : Geometry
    properties : MunicipalityProperties

class FeatureCollection(TypedDict):
    type     : Literal["FeatureCollection"]
    features : List[StateFeature] | List[MunicipalityFeature]