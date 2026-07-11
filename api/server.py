from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from typing import List, Dict

from db import repository
from api.models import State, Municipality, Geometry
from logging_config import setup_logging

# start api
app = FastAPI()

@app.get("/")
def welcome():
    return {"message" : "welcome"}

@app.get("/states")
def get_all_states() -> List[State]:
    states = repository.get_all_states()
    if states is None:
        raise HTTPException(404)
    return [
        State(**state) for state in states
    ]

@app.get("/states/{state_id}")
def get_state(state_id:int) -> State:
    state = repository.get_state(state_id)
    if state is None:
        raise HTTPException(404)
    state_name, state_capital = state
    return State(
        state_id=state_id,
        name=state_name,
        capital=state_capital
        )

@app.get("/states/{state_id}/geom")
def get_state_geom(state_id:int) -> Geometry:
    state_geom = repository.get_state_geometry(state_id)
    if state_geom is None:
        raise HTTPException(404)
    geom_type = state_geom["type"]
    coordinates = state_geom["coordinates"]
    return Geometry(
        geometry_type=geom_type,
        coordinates=coordinates
    )

@app.get("/states/{state_id}/municipalities")
def get_municipalities_of_state(state_id:int) -> List[Municipality]:
    municipalities = repository.get_municipalities(state_id)
    if municipalities is None:
        raise HTTPException(404)

    return [
        Municipality(name=name, municipality_id=municipality_id)
        for name, municipality_id
        in municipalities
    ]