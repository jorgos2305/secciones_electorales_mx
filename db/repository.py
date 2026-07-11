import psycopg2
from typing import Dict, Tuple
from pathlib import Path

from config import (
    DB_HOST,
    DB_NAME,
    DB_PASSWORD,
    DB_PORT,
    DB_USER
)

def get_connection() -> psycopg2.extensions.connection:
    return psycopg2.connect(f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}")

def get_state(state_id:int) -> Tuple | None:
    
    sql = """
    SELECT 
        name,
        capital,
        ST_AsGEOJSON(geometry)
    FROM
        state
    WHERE
        state_id = %s;
    """
    vars = (state_id,)
    with get_connection() as conn:
        with conn.cursor() as curs:
            curs.execute(sql, vars)
            state = curs.fetchone()
    return state