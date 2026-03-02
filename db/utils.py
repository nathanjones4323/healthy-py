import os

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Connection

from db.synchronous import get_engine


def init_db_connection() -> Connection:
    """Creates a SQLAlchemy connection object used to interact with a PostgreSQL DB.

    This now uses the pooled engine defined in `db.synchronous`.

    Returns:
        `sqlalchemy.engine.base.Connection`: SQLAlchemy connection object
    """
    try:
        engine = get_engine()
        conn = engine.connect()
        return conn
    except Exception as e:
        logger.error(f"Could not connect to DB: {str(e)}")
        raise


def init_metabase_db_connection() -> Connection:
    """Creates a SQLAlchemy connection object used to interact a postgres DB

    Returns:
        `sqlalchemy.engine.base.Connection`: SQLAlchemy connection object
    """
    engine = create_engine(
        url=f"postgresql://{os.getenv('MB_DB_USER')}:{os.getenv('MB_DB_PASS')}@{os.getenv('MB_DB_HOST')}:{os.getenv('MB_DB_PORT')}/{os.getenv('MB_DB_DBNAME')}"
    )
    conn = engine.connect()
    return conn
