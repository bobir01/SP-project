from datetime import datetime
from datetime import timezone, timedelta

def uni2dt(unix: float) -> datetime:
    """Convert a Unix timestamp to a datetime object with UTC+5
    :param unix: Unix timestamp.
    :return: Datetime object."""

    return datetime.utcfromtimestamp(unix).replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=5),
                                                                                             name='UTC+5'))

def format_float(f: float = None) -> str:
    """Format a float to a string with a given precision.
    :param f: Float to format.
    :param precision: Number of decimal places.
    :return: Formatted string."""
    return f"{f:.2f}" if f else "N/A"