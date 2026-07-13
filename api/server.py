from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from typing import List, Dict

from db import repository
from api.models import FeatureCollection, StateFeatureModel, StatePropertiesModel, GeometryModel, MunicipalityFeatureModel
from logging_config import setup_logging

# start api
app = FastAPI()

@app.get("/")
def welcome():
    return {"message" : "welcome"}

@app.get("/states")
def get_all_states() -> List[StatePropertiesModel]:
    states = repository.get_all_states()
    if states is None:
        raise HTTPException(404)
    return [
        StatePropertiesModel(**state) for state in states
    ]

@app.get("/states/{state_id}")
def get_state(state_id:int) -> StatePropertiesModel:
    state = repository.get_state(state_id)
    if state is None:
        raise HTTPException(404)
    return StatePropertiesModel(
        state_id=state["state_id"],
        name=state["name"],
        capital=state["capital"]
        )

@app.get("/states/{state_id}/geom")
def get_state_geom(state_id:int) -> StateFeatureModel:
    feature_dict = repository.get_state_geometry(state_id)
    if feature_dict is None:
        raise HTTPException(404)
    return StateFeatureModel(
        type=feature_dict["type"],
        geometry=GeometryModel(**feature_dict["geometry"]),
        properties=StatePropertiesModel(**feature_dict["properties"])
    )