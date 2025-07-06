from datetime import datetime
from db import get_all_entries

def convert_timestamp_to_readable(timestamp_str):
    """Convert timestamp to readable format"""
    try:
        # Assume timestamp is in milliseconds
        timestamp = int(timestamp_str) / 1000
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "Invalid timestamp"

def prepare_data_for_grid():
    """Prepare data with readable timestamps from database"""
    entries = get_all_entries()
    prepared_data = []
    for item in entries:
        prepared_item = item.copy()
        prepared_item["readable_time"] = convert_timestamp_to_readable(item["timestamp"])
        prepared_data.append(prepared_item)
    return prepared_data 