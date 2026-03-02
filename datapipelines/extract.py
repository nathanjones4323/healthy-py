try:
    from lxml import etree as ET
    HAS_LXML = True
except ImportError:
    import xml.etree.ElementTree as ET
    HAS_LXML = False

import pandas as pd
from loguru import logger


def extract_apple_health_data(path: str = "./data/apple_health_export/export.xml", start_date: str = None) -> pd.DataFrame:
    """
    Extract Apple Health data from XML file using streaming iterparse for memory efficiency.

    Args:
        path: Path to the XML file
        start_date: Optional date string to filter records (format: "YYYY-MM-DD")

    Returns:
        pd.DataFrame: DataFrame containing health records
    """
    try:
        # Parse start_date once for comparison
        # Use string comparison for ISO dates (much faster than parsing)
        start_date_str = None
        if start_date:
            # Normalize to ISO format for string comparison
            start_date_str = start_date if len(
                start_date) == 10 else start_date[:10]

        # Use iterparse for streaming parsing (memory efficient for large files)
        # This avoids loading the entire XML tree into memory
        record_list = []
        record_count = 0
        filtered_count = 0

        logger.info(f"Starting to parse XML file: {path}")
        if HAS_LXML:
            logger.info("Using lxml for parsing")
        else:
            logger.info(
                "Using standard library ElementTree for parsing")

        # Use iterparse with events to stream parse the XML
        # This is much more memory efficient than loading the entire tree
        context = ET.iterparse(path, events=('start', 'end'))
        context = iter(context)
        event, root = next(context)

        for event, elem in context:
            if event == 'end' and elem.tag == 'Record':
                # Filter by start_date during parsing to avoid processing unnecessary records
                if start_date_str is None:
                    # Copy attrib dict to avoid reference issues
                    record_list.append(dict(elem.attrib))
                    record_count += 1
                else:
                    # Use string comparison for ISO dates (much faster than parsing)
                    # Apple Health dates are in ISO format: "YYYY-MM-DD HH:MM:SS +HHMM"
                    record_start_date = elem.attrib.get('startDate', '')
                    if record_start_date:
                        # Compare first 10 chars (YYYY-MM-DD) as strings
                        # This is much faster than parsing dates
                        if record_start_date[:10] >= start_date_str:
                            record_list.append(dict(elem.attrib))
                            record_count += 1
                        else:
                            filtered_count += 1
                    else:
                        # No date, include it
                        record_list.append(dict(elem.attrib))
                        record_count += 1

                # Clear the element to free memory (important for large files)
                elem.clear()
                # Only clear root periodically to avoid overhead
                if record_count % 10000 == 0:
                    root.clear()

                # Log progress for large files
                if record_count % 100000 == 0:
                    logger.info(f"Parsed {record_count:,} records so far...")

        logger.info(f"Finished parsing. Total records: {record_count:,}")
        if filtered_count > 0:
            logger.info(
                f"Filtered out {filtered_count:,} records before start_date")
        logger.info("Creating DataFrame from parsed records...")

        # Create DataFrame more efficiently using from_records
        # This is faster than from_list of dicts for large datasets
        if record_list:
            # Pre-allocate if we know the size (slight optimization)
            data = pd.DataFrame.from_records(record_list)
        else:
            logger.warning("No records found in XML file")
            return pd.DataFrame()

        logger.success(
            f"Created DataFrame from Apple Health XML file: {data.shape[0]:,} rows, {data.shape[1]} columns")
        logger.debug(f"DataFrame dtypes: {data.dtypes}")

        return data

    except Exception as e:
        logger.error(f"Could not create DataFrame from Apple Health data: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return pd.DataFrame()


def extract_strong_app_data(path: str = "./data/strong_export/strong.csv", start_date: str = None) -> pd.DataFrame:
    try:
        data = pd.read_csv(path)
        if start_date:
            data = data[data['Date'] >= start_date]
        logger.success("Created DataFrame from Strong CSV file")
        logger.debug(f"Shape of DataFrame: {data.shape}")
        logger.debug(f"Data: {data}")
    except Exception as e:
        logger.error(f"Could not read Strong CSV file: {e}")
    return data
