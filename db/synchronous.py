import os
from contextlib import contextmanager
from io import StringIO

import pandas as pd
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

_ENGINE: Engine | None = None


def _detect_default_host() -> str:
    """Return a sensible default DB host for both local and Docker runs.

    Priority:
    1. If POSTGRES_HOST is set, always use it.
    2. If running inside Docker (/.dockerenv exists), use 'db' (docker-compose service).
    3. Otherwise, default to 'localhost' for local development.
    """
    explicit = os.getenv("POSTGRES_HOST")
    if explicit:
        return explicit

    if os.path.exists("/.dockerenv"):
        return "db"

    return "localhost"


def _build_database_url() -> str:
    """Build the SQLAlchemy database URL using psycopg3."""
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = _detect_default_host()
    port = os.getenv("POSTGRES_PORT")
    db = os.getenv("POSTGRES_DB")

    if not all([user, password, port, db]):
        raise RuntimeError(
            "Database environment variables are not fully set. "
            "Expected POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_PORT, POSTGRES_DB."
        )

    # Use psycopg3 driver explicitly
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"


def get_engine() -> Engine:
    """Return a singleton SQLAlchemy Engine with an internal connection pool."""
    global _ENGINE
    if _ENGINE is not None:
        return _ENGINE

    url = _build_database_url()
    logger.info("Creating PostgreSQL engine with connection pool (psycopg3)...")

    _ENGINE = create_engine(
        url,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=1800,  # recycle connections periodically
        echo=False,
        future=True,
    )
    return _ENGINE


@contextmanager
def get_connection():
    """Context manager that yields a pooled SQLAlchemy Connection."""
    engine = get_engine()
    with engine.connect() as conn:
        yield conn


def dispose_engine():
    """Dispose the global engine and its connection pool (useful for tests)."""
    global _ENGINE
    if _ENGINE is not None:
        _ENGINE.dispose()
        _ENGINE = None


def copy_dataframe_to_table(
    df: pd.DataFrame,
    table_name: str,
    schema: str = "public",
) -> None:
    """Efficiently load a large DataFrame into PostgreSQL using COPY.

    This uses the pooled psycopg3-backed SQLAlchemy engine and streams the
    DataFrame as CSV into a COPY command, which is significantly faster than
    row-by-row INSERTs or plain `to_sql` for ~GB-sized loads.
    """
    if df is None or df.empty:
        logger.warning(
            f"Skipping COPY for {table_name} - dataframe is None or empty")
        return

    engine = get_engine()

    # Prepare CSV in-memory; use \N as NULL representation for PostgreSQL
    buffer = StringIO()
    df.to_csv(buffer, index=False, header=False, na_rep="\\N")
    buffer.seek(0)

    columns = ", ".join(f'"{col}"' for col in df.columns)
    full_table_name = f'"{schema}"."{table_name}"'
    copy_sql = (
        f"COPY {full_table_name} ({columns}) "
        "FROM STDIN WITH (FORMAT CSV, NULL '\\N')"
    )

    logger.info(
        f"Starting COPY of {df.shape[0]:,} rows into {schema}.{table_name} using pooled connection..."
    )

    # Use raw psycopg3 connection underneath the SQLAlchemy engine
    raw_conn = engine.raw_connection()
    try:
        with raw_conn.cursor() as cur:
            # psycopg3 no longer exposes `copy_expert`; instead it provides a
            # `copy()` context manager for COPY operations.
            with cur.copy(copy_sql) as copy:
                # Stream the CSV buffer in chunks to avoid holding an extra
                # huge string in memory.
                buffer.seek(0)
                for chunk in iter(lambda: buffer.read(1024 * 1024), ""):
                    if not chunk:
                        break
                    copy.write(chunk.encode())
        raw_conn.commit()
    except Exception:
        raw_conn.rollback()
        raise
    finally:
        # `engine.raw_connection()` returns SQLAlchemy's _ConnectionFairy in some
        # versions, which is not a context manager; always close explicitly.
        raw_conn.close()

    logger.success(
        f"Finished COPY of {df.shape[0]:,} rows into {schema}.{table_name}"
    )


def create_raw_tables() -> None:
    """Create (or recreate) the raw Apple Health and Strong tables using explicit DDL."""
    engine = get_engine()

    apple_health_activity_sql = """
    DROP TABLE IF EXISTS apple_health_activity_raw;
    CREATE TABLE apple_health_activity_raw (
        end_date timestamp with time zone,
        creation_date timestamp with time zone,
        start_date timestamp with time zone,
        source_name text,
        active_energy_burned double precision,
        apple_exercise_time double precision,
        apple_sleeping_wrist_temperature double precision,
        apple_stand_hour double precision,
        apple_stand_time double precision,
        apple_walking_steadiness double precision,
        audio_exposure_event double precision,
        basal_energy_burned double precision,
        body_mass double precision,
        distance_cycling double precision,
        distance_swimming double precision,
        distance_walking_running double precision,
        environmental_audio_exposure double precision,
        environmental_sound_reduction double precision,
        flights_climbed double precision,
        headphone_audio_exposure double precision,
        heart_rate double precision,
        heart_rate_recovery_one_minute double precision,
        heart_rate_variability_s_d_n_n double precision,
        high_heart_rate_event double precision,
        oxygen_saturation double precision,
        physical_effort double precision,
        respiratory_rate double precision,
        resting_heart_rate double precision,
        running_ground_contact_time double precision,
        running_power double precision,
        running_speed double precision,
        running_stride_length double precision,
        running_vertical_oscillation double precision,
        six_minute_walk_test_distance double precision,
        sleep_analysis double precision,
        sleep_duration_goal double precision,
        stair_ascent_speed double precision,
        stair_descent_speed double precision,
        step_count double precision,
        swimming_stroke_count double precision,
        time_in_daylight double precision,
        v_o2_max double precision,
        walking_asymmetry_percentage double precision,
        walking_double_support_percentage double precision,
        walking_heart_rate_average double precision,
        walking_speed double precision,
        walking_step_length double precision
    );
    """

    strong_app_sql = """
    DROP TABLE IF EXISTS strong_app_raw;
    CREATE TABLE strong_app_raw (
        created_at timestamp without time zone,
        workout_name text,
        duration bigint,
        exercise_name text,
        set_order text,
        weight double precision,
        reps double precision,
        distance bigint,
        seconds double precision,
        notes double precision,
        workout_notes double precision,
        r_p_e double precision,
        workout_id text
    );
    """

    apple_health_sleep_sql = """
    DROP TABLE IF EXISTS apple_health_sleep_raw;
    CREATE TABLE apple_health_sleep_raw (
        creation_date timestamp with time zone,
        total_time_asleep_seconds double precision,
        bed_time timestamp with time zone,
        awake_time timestamp with time zone,
        sleep_counts bigint,
        rem_cycles bigint,
        time_in_bed_seconds double precision,
        restless_time_seconds double precision
    );
    """

    logger.info("Creating/recreating raw tables: apple_health_activity_raw, strong_app_raw, apple_health_sleep_raw...")
    with engine.begin() as conn:
        conn.exec_driver_sql(apple_health_activity_sql)
        conn.exec_driver_sql(strong_app_sql)
        conn.exec_driver_sql(apple_health_sleep_sql)
    logger.success("Finished creating raw tables.")
