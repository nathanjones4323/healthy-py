import os
import time

from dotenv import load_dotenv
from loguru import logger

from db.synchronous import copy_dataframe_to_table, get_engine

# Load environment variables from the .env file
# os.path.dirname(__file__): Gives you the directory of your Python script.
# ..: Moves up one level to the parent directory.
# 'db': Enters the db directory.
# '.env': Specifies the .env file you want to access.
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'db', '.env')
try:
    load_dotenv(dotenv_path)
    logger.success("Loaded .env file")
except Exception:
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

        # Bulk load with COPY via psycopg3 for maximum throughput.
        copy_dataframe_to_table(
            transformed_data, table_name=table_name, schema="public")
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

        copy_dataframe_to_table(
            transformed_data, table_name="strong_app_raw", schema="public"
        )
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
