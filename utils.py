from datetime import datetime


def uni2dt(uni: float) -> datetime:
    """Convert a Unix timestamp to a datetime object.
    :param uni: Unix timestamp.
    :return: Datetime object."""
    return datetime.utcfromtimestamp(uni)

def format_float(f: float = None) -> str:
    """Format a float to a string with a given precision.
    :param f: Float to format.
    :param precision: Number of decimal places.
    :return: Formatted string."""
    return f"{f:.2f}" if f else "N/A"