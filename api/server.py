from fastapi import FastAPI
from fastapi.exceptions import HTTPException
import json

from db import repository
from api.models import State
from logging_config import setup_logging

# start api
app = FastAPI()

@app.get("/")
def welcome():
    return {"message" : "welcome"}

@app.get("/states/{state_id}")
def get_state(state_id:int) -> State:
    state = repository.get_state(state_id)
    if state is None:
        raise HTTPException(404)
    state_name, state_capital, state_geometry = state
    return State(
        name=state_name,
        capital=state_capital,
        geometry=json.loads(state_geometry)
        )