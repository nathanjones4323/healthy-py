import xml.etree.ElementTree as ET

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
        start_date_dt = None
        if start_date:
            start_date_dt = pd.to_datetime(start_date)

        # Use iterparse for streaming parsing (memory efficient for large files)
        # This avoids loading the entire XML tree into memory
        record_list = []
        record_count = 0

        logger.info(f"Starting to parse XML file: {path}")

        # Use iterparse with events to stream parse the XML
        # This is much more memory efficient than loading the entire tree
        context = ET.iterparse(path, events=('start', 'end'))
        context = iter(context)
        event, root = next(context)

        for event, elem in context:
            if event == 'end' and elem.tag == 'Record':
                # Filter by start_date during parsing to avoid processing unnecessary records
                if start_date_dt is None:
                    record_list.append(elem.attrib)
                    record_count += 1
                else:
                    # Only add record if it meets the date filter
                    record_start_date = elem.attrib.get('startDate')
                    if record_start_date:
                        try:
                            if pd.to_datetime(record_start_date) >= start_date_dt:
                                record_list.append(elem.attrib)
                                record_count += 1
                        except (ValueError, TypeError):
                            # If date parsing fails, include the record anyway
                            record_list.append(elem.attrib)
                            record_count += 1
                    else:
                        record_list.append(elem.attrib)
                        record_count += 1

                # Clear the element to free memory (important for large files)
                elem.clear()
                root.clear()

                # Log progress for large files
                if record_count % 100000 == 0:
                    logger.info(f"Parsed {record_count:,} records so far...")

        logger.info(f"Finished parsing. Total records: {record_count:,}")
        logger.info("Creating DataFrame from parsed records...")

        # Create DataFrame more efficiently using from_records
        # This is faster than from_list of dicts for large datasets
        if record_list:
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
