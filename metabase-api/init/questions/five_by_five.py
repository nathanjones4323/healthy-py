from init.questions.utils import create_sql_question, set_visualization_settings
from metabase_api import Metabase_API
from queries.five_by_five.progressive_overload import query_progressive_overload


def five_by_five_progressive_overload(mb: Metabase_API):
    query = query_progressive_overload()
    visualization_settings = set_visualization_settings(
        dimensions=["last_lift_performed_at", "exercise_name", "number_of_sets", "number_of_reps",
                    "last_working_set_weight", "new_working_set_weight", "increase_weight"],
        metrics=["last_lift_performed_at", "exercise_name", "number_of_sets", "number_of_reps",
                 "last_working_set_weight", "new_working_set_weight", "increase_weight"]
    )
    create_sql_question(mb, query=query, question_name="5x5 Progressive Overload - New Working Set Weight",
                        display="table", db_id=2, collection_id=7, table_id=50, visualization_settings=visualization_settings)
