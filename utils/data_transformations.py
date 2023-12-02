import datetime


def datetime_converter(data):
    """
    Converts datetime objects to ISO format, and recursively applies to lists and dictionaries.
    
    Args:
        data (datetime|list|dict): The data to convert.
        
    Returns:
        The data in a format that can be serialized to JSON.
    """
    if isinstance(data, datetime.datetime):
        return data.isoformat()
    elif isinstance(data, dict):
        return {key: datetime_converter(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [datetime_converter(item) for item in data]
    else:
        return data
