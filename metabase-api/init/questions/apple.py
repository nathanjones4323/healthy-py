from init.questions.utils import (
    create_sql_timeseries_question,
    set_visualization_settings,
)
from metabase_api import Metabase_API
from queries.apple.activity import query_calories_burned
from queries.apple.sleep import query_rem_cycles, query_sleep_hours


def apple_calories(mb: Metabase_API):
    query = query_calories_burned()
    visualization_settings = set_visualization_settings(
        x_axis_title="Time Period",
        y_axis_title="Calories Burned",
        dimensions=["time_period"],
        metrics=["total_calories_burned",
                 "active_calories_burned", "resting_calories_burned"]
    )
    create_sql_timeseries_question(mb, query=query, question_name="Calories Burned Over Time",
                                   display="line", db_id=2, collection_id=6, table_id=40, visualization_settings=visualization_settings)


def apple_sleep_hours(mb: Metabase_API):
    query = query_sleep_hours()
    visualization_settings = set_visualization_settings(
        x_axis_title="Time Period",
        y_axis_title="Hours",
        dimensions=["time_period"],
        metrics=["hours_of_sleep", "average_hours_of_sleep",
                 "hours_of_time_in_bed", "average_hours_of_time_in_bed", "average_rem_cycles"]
    )
    create_sql_timeseries_question(mb, query=query, question_name="Hours of Sleep Over Time",
                                   display="line", db_id=2, collection_id=6, table_id=49, visualization_settings=visualization_settings)


def apple_rem_cycles(mb: Metabase_API):
    query = query_rem_cycles()
    visualization_settings = set_visualization_settings(
        x_axis_title="Time Period",
        y_axis_title="Average REM Cycles",
        dimensions=["time_period"],
        metrics=["average_rem_cycles", "rem_cycles"]
    )
    create_sql_timeseries_question(mb, query=query, question_name="REM Cycles Over Time",
                                   display="line", db_id=2, collection_id=6, table_id=33, visualization_settings=visualization_settings)
