import psycopg2
import json
from typing import TypedDict, Dict, Tuple, List, Literal, Any
from pathlib import Path

from config import (
    DB_HOST,
    DB_NAME,
    DB_PASSWORD,
    DB_PORT,
    DB_USER
)

class GeoJSON(TypedDict):
    """
    This class help assign the correct data types to the dictionary of coordinates returned by the database.
    It used together with the Geometry model for the correct format of the API responses.
    See models.py and server.py

    Args:
        TypedDict : A dictionary containing the information about the geometry of the land.
    """
    type : Literal["Polygon", "MultiPolygon"]
    coordinates : List[Any]

class State(TypedDict):
    state_id : int
    name     : str
    capital  : str | None

def _get_connection() -> psycopg2.extensions.connection:
    """
    Helper private method to connect to the database.

    Returns:
        psycopg2.extensions.connection: a connection object.
    """
    return psycopg2.connect(f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}")

def get_all_states() -> List[State] | None:
    """_summary_

    Returns:
        List[State]: _description_
    """
    sql = """
    SELECT
        state_id,
        name,
        capital
    FROM
        state;
    """
    with _get_connection() as conn:
        with conn.cursor() as curs:
            curs.execute(sql)
            states = curs.fetchall()
    if not states:
        return None
    return [
        State(state_id=state_id, name=name, capital=capital)
        for state_id, name, capital
        in states
    ]

def get_state(state_id:int) -> Tuple[str, str | None] | None:
    """
    Get a state from the database by its id.
    The id corresponsed to the ID given by the INE to the corresponding state.
    """
    sql = """
    SELECT 
        name,
        capital
    FROM
        state
    WHERE
        state_id = %s;
    """
    vars = (state_id,)
    with _get_connection() as conn:
        with conn.cursor() as curs:
            curs.execute(sql, vars)
            state = curs.fetchone()
    return state

def get_state_geometry(state_id:int) -> GeoJSON | None:
    """
    Get the geometry data for a specific state.

    Args:
        state_id (int): ID of the corresponding state. Matches IDs given by the INE.

    Returns:
        GeoJSON | None: Geometry data.
    """

    sql = """
    SELECT
        ST_AsGEOJSON(geometry)
    FROM
        state
    WHERE
        state_id = %s;
    """

    vars = (state_id,)
    with _get_connection() as conn:
        with conn.cursor() as curs:
            curs.execute(sql, vars)
            # the DB returns a tuple with the geometry data as a string
            state_geom = curs.fetchone()
    if state_geom is None:
        return state_geom
    return GeoJSON(
        **json.loads(state_geom[0])
    )

def get_municipalities(state_id:int) -> List[Tuple[str, int]] | None:
    """_summary_

    Args:
        state_id (int): _description_

    Returns:
        List: _description_
    """

    sql = """
    SELECT 
        municipality.name,
        municipality.municipality_id
    FROM
        municipality
    WHERE
        municipality.state_id = %s;
    """
    vars = (state_id,)
    with _get_connection() as conn:
        with conn.cursor() as curs:
            curs.execute(sql, vars)
            municipalities = curs.fetchall()
    if not municipalities:
        return None
    return sorted(municipalities, key=lambda m: m[1])