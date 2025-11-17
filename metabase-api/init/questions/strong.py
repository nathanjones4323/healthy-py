from init.questions.utils import (
    create_sql_question,
    create_sql_timeseries_question,
    set_visualization_settings,
)
from metabase_api import Metabase_API
from queries.strong.lifting import (
    query_count_by_workout_type,
    query_duration_by_workout_type,
    query_sets_by_exercise_type,
    query_sets_by_workout_type,
)


def strong_workout_duration_by_type(mb: Metabase_API):
    query = query_duration_by_workout_type()
    visualization_settings = set_visualization_settings(
        x_axis_title="Workout Type",
        y_axis_title="Avg. Workout Duration (min)",
        dimensions=["workout_name"],
        metrics=["average_workout_length_minutes",
                 "median_workout_length_minutes"]
    )
    create_sql_question(mb, query=query, question_name="Workout Duration by Type",
                        display="bar", db_id=2, collection_id=5, table_id=50, visualization_settings=visualization_settings, timestamp_field_name="created_at")


def strong_sets_by_workout_type(mb: Metabase_API):
    query = query_sets_by_workout_type()
    visualization_settings = set_visualization_settings(
        x_axis_title="Time Period",
        y_axis_title="Number of Sets",
        dimensions=["time_period", "workout_name"],
        metrics=["number_of_sets"]
    )
    create_sql_timeseries_question(mb, query=query, question_name="Sets Over Time",
                                   display="line", db_id=2, collection_id=5, table_id=50, visualization_settings=visualization_settings)


def strong_volume_by_exercise_type(mb: Metabase_API):
    query = query_sets_by_exercise_type()
    visualization_settings = set_visualization_settings(
        dimensions=["time_period", "exercise_name"],
        metrics=["time_period", "exercise_name"]
    )
    create_sql_timeseries_question(mb, query=query, question_name="Sets by Exercise Type Over Time",
                                   display="table", db_id=2, collection_id=5, table_id=50, visualization_settings=visualization_settings)


def strong_count_by_workout_type(mb: Metabase_API):
    query = query_count_by_workout_type()
    visualization_settings = set_visualization_settings(
        x_axis_title="Time Period",
        y_axis_title="Number of Workouts",
        dimensions=["time_period", "workout_name"],
        metrics=["number_of_workout_days"]
    )
    create_sql_timeseries_question(mb, query=query, question_name="Workouts Over Time by Type",
                                   display="line", db_id=2, collection_id=5, table_id=50, visualization_settings=visualization_settings)
