import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
# load env variables
env_loaded = load_dotenv(".env")
if not env_loaded:
    logger.error("Could not load .env")
    raise RuntimeError("Could not load .env - Check whether file exists.")
else:
    logger.info("Loaded .env file sucessfully")
    DB_NAME = os.getenv("DB_NAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_USER = os.getenv("DB_USER")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    APP_HOST = os.getenv("APP_HOST")