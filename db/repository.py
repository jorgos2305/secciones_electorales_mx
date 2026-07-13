import psycopg2
import json
from typing import TypedDict, Tuple, List, Literal, Any
from pathlib import Path

from db.schemas import (
    Geometry,
    StateProperties,
    MunicipalityProperties,
    StateFeature,
    MunicipalityFeature,
    FeatureCollection
)
from config import (
    DB_HOST,
    DB_NAME,
    DB_PASSWORD,
    DB_PORT,
    DB_USER
)


def _row_to_state_feature(row:Tuple[int, str, str | None, str]) -> StateFeature:
    state_id, name, capital, geometry = row
    return {
        "type"       : "Feature",
        "geometry"   : json.loads(geometry),
        "properties" : {
            "state_id" : state_id,
            "name"     : name,
            "capital"  : capital
        }
    }

def _row_to_municipality_feature(row:Tuple[int, int, int, str, str]) -> MunicipalityFeature:
    municipality_db_id, municipality_id, state_id, name, geometry = row
    return {
        "type"       : "Feature",
        "geometry"   : json.loads(geometry),
        "properties" : {
            "municipality_db_id" : municipality_db_id,
            "municipality_id"    : municipality_id,
            "state_id"           : state_id,
            "name"               : name
        }
    }

def _get_connection() -> psycopg2.extensions.connection:
    """
    Helper private method to connect to the database.

    Returns:
        psycopg2.extensions.connection: a connection object.
    """
    return psycopg2.connect(f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}")

def get_all_states() -> List[StateProperties] | None:
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
        {
            "state_id" : state_id,
            "name" : name,
            "capital" : capital
        }
        for state_id, name, capital in states
    ]

def get_all_states_geom() -> FeatureCollection | None:
    sql = """
    SELECT
        state_id,
        name,
        capital,
        ST_AsGEOJSON(geometry)
    FROM
        state;
    """
    # get rows from database    
    with _get_connection() as conn:
        with conn.cursor() as curs:
            curs.execute(sql)
            rows = curs.fetchall()
    # nothing is returned from the database
    if not rows:
        return None
    # FeatureCollection
    features = [_row_to_state_feature(row) for row in rows]
    return {
        "type" : "FeatureCollection",
        "features" : features
    }
    
def get_state(state_id:int) -> StateProperties | None:
    sql = """
    SELECT
        state_id, 
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
            row = curs.fetchone()
    if row is None:
        return row
    state_db_id, name, capital = row
    return {
        "state_id" : state_db_id,
        "name"     : name,
        "capital"  : capital
    }

def get_state_geometry(state_id:int) -> StateFeature | None:
    sql = """
    SELECT
        state_id,
        name,
        capital,
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
            row = curs.fetchone()
    if row is None:
        return row
    return _row_to_state_feature(row)

def get_all_municipalities(state_id:int) -> List[MunicipalityProperties] | None:
    sql = """
    SELECT 
        id,
        municipality_id,
        state_id,
        name
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
    return [
        {"municipality_db_id" : compose_id,
         "municipality_id"    : municipality_id,
         "state_id"           : municipality_state_id,
         "name"               : name}
         for compose_id, municipality_id, municipality_state_id, name in municipalities
    ]
    
def get_all_municipalities_geom(state_id:int) -> FeatureCollection | None:
    raise NotImplementedError

def get_all_sections(municipality_id:int) -> List[MunicipalityProperties] | None:
    raise NotImplementedError

if __name__ == "__main__":

    states = get_all_states_geom()
    if states is not None:     
        with Path(__file__).parent.joinpath("test.json").open("w") as out:
            json.dump(states, out, indent=4)
