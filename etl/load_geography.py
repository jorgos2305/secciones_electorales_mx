import pandas as pd
import geopandas as gpd
import psycopg2
import logging
import os
from shapely.geometry import Polygon, MultiPolygon
from dotenv import load_dotenv
from pathlib import Path
from typing import Tuple, List, Dict

from logging_config import setup_logging

# Set up the logs
setup_logging(log_file="load_geography.log")
logger = logging.getLogger(__name__)

def normalize_geometry(geom: Polygon | MultiPolygon) -> MultiPolygon:
    if isinstance(geom, Polygon):
        return MultiPolygon([geom])
    return geom

def clean_df(df_list:List[gpd.GeoDataFrame], sort_key:List[str], drop_cols:List[str], rename_cols:Dict[str, str]) -> pd.DataFrame:
    df = pd.concat(df_list).sort_values(by=sort_key, ignore_index=True)
    df = df.drop(drop_cols, axis=1)
    df = df.rename(columns=rename_cols)
    return df

def get_geography(root:Path) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    states = []
    municipalities = []
    secciones = []

    for folder in root.iterdir():
        if folder.name.startswith("."):
            continue # ignore all hidden files
        # the 32 federal states
        state = gpd.read_file(folder.joinpath("ENTIDAD.shp")).to_crs("EPSG:4326")
        states.append(state)
        # municipalities of the federal states
        municipality = gpd.read_file(folder.joinpath("MUNICIPIO.shp")).to_crs("EPSG:4326")
        municipalities.append(municipality)
        # electoral sections of each municipality
        seccion = gpd.read_file(folder.joinpath("SECCION.shp")).to_crs("EPSG:4326")
        secciones.append(seccion)
    states = clean_df(
        states,
        sort_key = ["entidad"],
        drop_cols = ["id", "circunscri", "crc", "control"],
        rename_cols = {"entidad":"id"}
    )
    states["capital"] = None
    states = states.loc[:, ["id", "nombre", "capital", "geometry"]]
    states["geometry"] = states["geometry"].apply(normalize_geometry) # type: ignore

    municipalities = clean_df(
        municipalities,
        sort_key=["entidad", "municipio"],
        drop_cols=["id", "control"],
        rename_cols={"municipio":"id"}
    )
    secciones = clean_df(
        secciones,
        sort_key=["entidad", "municipio", "seccion"],
        drop_cols=["id", "tipo", "control"],
        rename_cols={"seccion":"id"}
    )
    return states, municipalities, secciones

def create_tables(conn:psycopg2.extensions.connection) -> None:
    schema = Path(__file__).parents[1] / "db" / "schema.sql"
    with schema.open() as table_schemas:
        sql = table_schemas.read()
    
    try:
        with conn.cursor() as curs:
            curs.execute(sql)
            logger.info("Tables sucessfully created")
    except Exception as exc:
        logger.error(f"Could not create tables: {exc}")
        raise RuntimeError("Could not create tables") from exc

def insert_states(conn:psycopg2.extensions.connection, states:pd.DataFrame) -> None:
    
    rows = [
        (
            row.id,
            row.nombre,
            row.capital,
            row.geometry.wkt if row.geometry else None # type: ignore
        )
        for row in states.itertuples(index=False)
    ]
    sql = """
    INSERT INTO state (state_id, name, capital, geometry)
    VALUES (%s, %s, %s, ST_GeomFromText(%s, 4326));
    """
    try:
        with conn.cursor() as curs:
            curs.executemany(sql, rows)
            logger.info("Rows sucessfully inserted into table: states")
    except Exception as exc:
        logger.info("Could not insert rows into table: states")
        raise RuntimeError("Could not insert rows into table: states") from exc

def insert_municipalities(conn:psycopg2.extensions.connection, municipalities:pd.DataFrame) -> None:
    raise NotImplementedError

def insert_secciones(conn:psycopg2.extensions.connection, secciones:pd.DataFrame) -> None:
    raise NotImplementedError

if __name__ == "__main__":

    env_path = Path(__file__).parents[2] / ".env"
    load_dotenv(r"/Users/jorgetellez/Documents/06_Projects/secciones_electorales_mx/.env")
    DB_NAME = os.getenv("DB_NAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_USER = os.getenv("DB_USER")
    DB_HOST = os.getenv("DB_HOST")

    # Get the raw data and place it in the database
    data_root = Path(f"data/raw/")

    states, municipalities, secciones = get_geography(data_root)
    
    with psycopg2.connect(f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port=5432") as conn:
        logger.info("Create tables")
        create_tables(conn)
        logger.info("Insert states")
        insert_states(conn, states)
        #logger.info("Insert municipalities")
        #insert_municipalities(conn, municipalities)
        #logger.info("Insert secciones")
        #insert_secciones(conn, secciones)