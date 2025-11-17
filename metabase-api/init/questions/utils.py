import re
import uuid

from filters.utils import add_field_filters, get_field_mappings
from loguru import logger
from metabase_api import Metabase_API


def set_visualization_settings(show_values: bool = True, x_axis_title: str = None, y_axis_title: str = None, dimensions: list = None, metrics: list = None):
    """Sets the visualization settings for a Metabase question.

    Args:
        show_values (bool, optional): True to show the data points in a visual, False to hide them. Defaults to True.
        x_axis_title (str, optional): The title of the x-axis. Defaults to None, which will use the SQL column name.
        y_axis_title (str, optional): The title of the y-axis. Defaults to None, which will leave the y-axis untitled.
        dimensions (list, optional): The variables to group on / have on the x-axis (order matters). Defaults to None.
        metrics (list, optional): The variables to plot (order matters). Defaults to None.

    Returns:
        dict: A dictionary of the visualization settings to be passed to the `create_sql_question` and `create_sql_timeseries_question` functions.
    """
    visualization_settings = {
        "graph.show_values": show_values,
        "graph.x_axis.title_text": x_axis_title,
        "graph.y_axis.title_text": y_axis_title,
        "graph.dimensions": dimensions,
        "graph.metrics": metrics
    }
    return visualization_settings


def create_sql_question(mb: Metabase_API, query: str, display: str = "table", question_name: str = "test_card", db_id: int = 2, collection_id: int = 4, table_id: int = 48, visualization_settings: dict = None, timestamp_field_name: str = "created_at"):
    try:
        # Parse the table name from the query
        table_name = query.split("from")[1].strip().split("\n")[0]
        # Get the field mappings
        field_mappings = get_field_mappings(mb=mb, table_field_tuples=[
                                            (table_name, timestamp_field_name)])
        # Pull out field data from the field mappings
        field_id = field_mappings[0]["field_id"]
        field_name = field_mappings[0]["field_name"]
        field_display_name = field_mappings[0]["field_display_name"]

    except Exception as e:
        logger.error(f"Could not parse table name from query: {e}")
        logger.debug(f"Query: {query}")

    my_custom_json = {
        'name': question_name,
        "display": display,
        'dataset_query': {
            'database': db_id,
            'native': {
                'query': query.strip(),
                'template-tags': {
                    field_name:
                        {"type": "dimension",
                         "name": field_name,
                         "id": str(uuid.uuid4()),
                         "display-name": field_display_name,
                         "dimension": ["field", field_id, None],
                         "widget-type": "date/all-options"}
                }
            },
            'type': 'native',
        },
        "visualization_settings": visualization_settings
    }

    try:
        api_response = mb.create_card(question_name, db_id=db_id, collection_id=collection_id,
                                      table_id=table_id, custom_json=my_custom_json)
        logger.success(f"Successfully created question - {question_name}")
    except Exception as e:
        logger.error(f"Could not create question - {question_name}\n{e}")


def create_sql_timeseries_question(mb: Metabase_API, query: str, display: str = "table", question_name: str = "test_card", db_id: int = 2, collection_id: int = 4, table_id: int = 48, visualization_settings: dict = None):
    try:
        # Parse the table name from the query
        table_name = query.split("from")[1].strip().split("\n")[0]

        # Extract filter references
        filter_references = re.findall(r'\[\[\s+and\s+{{(\w+)}}\s+\]\]', query)

        # CAN USE THIS ONCE MIN MAX FILTERS ARE ADDED TO THE STRONG APP
        # filter_references = re.findall(r"\{\{(\w+)\}\}", query)
        # filter_references.remove("date_granularity")

        # Create a list of tuples of the table name and the filter reference
        table_filter_tuples = [(table_name, filter_reference)
                               for filter_reference in filter_references]

        # Get the field mappings
        field_mappings = get_field_mappings(
            mb=mb, table_field_tuples=table_filter_tuples)

    except Exception as e:
        logger.error(f"Could not parse table name from query: {e}")
        logger.debug(f"Query: {query}")

    # Create the payload for the Metabase API post request
    my_custom_json = {
        'name': question_name,
        "display": display,
        'dataset_query': {
            'database': db_id,
            'native': {
                'query': query.strip(),
                'template-tags': {
                    "date_granularity":
                        {"type": "text",
                         "name": "date_granularity",
                         "id": str(uuid.uuid4()),
                         "display-name": "Date Granularity",
                         "required": True,
                         "default": ["Week"]}
                }
            },
            'type': 'native',
        },
        "visualization_settings": visualization_settings
    }
    # Add the field filters to the payload (template-tags)
    my_custom_json = add_field_filters(
        mappings=field_mappings, my_custom_json=my_custom_json)

    try:
        api_response = mb.create_card(question_name, db_id=db_id, collection_id=collection_id,
                                      table_id=table_id, custom_json=my_custom_json)
        logger.success(f"Successfully created question - {question_name}")
    except Exception as e:
        logger.error(f"Could not create question - {question_name}\n{e}")
