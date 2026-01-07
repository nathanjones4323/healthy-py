import os
import time

from dotenv import load_dotenv
from loguru import logger

from db.utils import init_db_connection

# Load environment variables from the .env file
# os.path.dirname(__file__): Gives you the directory of your Python script.
# ..: Moves up one level to the parent directory.
# 'db': Enters the db directory.
# '.env': Specifies the .env file you want to access.
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'db', '.env')
try:
    load_dotenv(dotenv_path)
    logger.success("Loaded .env file")
except:
    logger.error("Could not load .env file")


def load_apple_health_data(transformed_data, table_name="apple_health_activity_raw"):
    try:
        if transformed_data is None or transformed_data.empty:
            logger.warning(
                f"Skipping load for {table_name} - dataframe is None or empty")
            return

        row_count = transformed_data.shape[0]
        logger.info(
            f"Starting to load {row_count:,} rows into {table_name} table...")

        conn = init_db_connection()
        if conn is None:
            logger.error(
                f"Could not establish database connection for {table_name}")
            return

        # Get the engine from the connection for better performance
        engine = conn.engine

        # For large datasets, use a larger chunksize and method='multi'
        # method='multi' uses executemany() which is faster than individual inserts
        # Larger chunksize reduces round trips but uses more memory
        # Adaptive chunksize
        chunksize = min(50000, max(10000, row_count // 20))

        logger.info(f"Using chunksize of {chunksize:,} for loading...")

        # Write to Database with method='multi' for better performance on large datasets
        # Using engine directly allows better connection management
        transformed_data.to_sql(
            name=table_name,
            con=engine,  # Use engine instead of connection for better performance
            schema="public",
            if_exists="replace",
            index=False,  # Don't create index column if not needed (faster)
            method='multi',
            chunksize=chunksize
        )

        # Close out DB connection
        conn.close()
        logger.success(
            f"Loaded {row_count:,} rows of Apple Health data to DB into the {table_name} table")
    except Exception as e:
        logger.error(
            f"Could not load Apple Health data to DB into the {table_name} table: {e}")
        import traceback
        logger.error(traceback.format_exc())


def load_strong_app_data(transformed_data):
    try:
        if transformed_data is None or transformed_data.empty:
            logger.warning(
                "Skipping load for strong_app_raw - dataframe is None or empty")
            return

        row_count = transformed_data.shape[0]
        logger.info(
            f"Starting to load {row_count:,} rows into strong_app_raw table...")

        conn = init_db_connection()
        if conn is None:
            logger.error(
                "Could not establish database connection for strong_app_raw")
            return

        # Get the engine from the connection for better performance
        engine = conn.engine

        # Adaptive chunksize based on data size
        chunksize = min(50000, max(10000, row_count // 20))

        # Write to Database with method='multi' for better performance
        transformed_data.to_sql(
            name="strong_app_raw",
            con=engine,  # Use engine instead of connection
            schema="public",
            if_exists="replace",
            index=False,  # Don't create index column if not needed
            method='multi',
            chunksize=chunksize
        )
        # Close out DB connection
        conn.close()
        logger.success(
            f"Loaded {row_count:,} rows of Strong App data to DB")
    except Exception as e:
        logger.error(f"Could not load Strong App data to DB: {e}")
        import traceback
        logger.error(traceback.format_exc())


# Add a 10 second delay to allow the Metabase backend to start before trying to connect to it
logger.info("Waiting for Metabase backend to start...")
for i in range(10):
    time.sleep(1)
    i = 11 - i
    if i % 5 == 0:
        logger.info(
            f"Waiting for Metabase backend to start... {i} seconds remaining")
