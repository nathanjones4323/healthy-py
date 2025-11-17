import time

from loguru import logger

from datapipelines.extract import extract_apple_health_data, extract_strong_app_data
from datapipelines.load import load_apple_health_data, load_strong_app_data
from datapipelines.transform import (
    split_apple_health_data,
    transform_apple_health_data,
    transform_strong_data,
)

# Create a new logger
logger.add("logs/log_{time}.log", rotation="500 MB", compression="zip")

# Extract data
apple_data = extract_apple_health_data(start_date="2023-09-05")
strong_data = extract_strong_app_data(start_date="2023-01-01")

# Transform data
apple_health_df = transform_apple_health_data(apple_data)
apple_health_sleep_df, apple_health_activity_df = split_apple_health_data(
    apple_health_df)
strong_df = transform_strong_data(strong_data)

# Load data
load_apple_health_data(apple_health_sleep_df,
                       table_name="apple_health_sleep_raw")
load_apple_health_data(apple_health_activity_df,
                       table_name="apple_health_activity_raw")
load_strong_app_data(strong_df)
